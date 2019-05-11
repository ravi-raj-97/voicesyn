"""
Date: 7-5-2019
Description: Script to create a list of sounds given a single audio file and the text transcript and store in given directory
"""

import multiprocessing
import json
import gentle
from pydub import AudioSegment, exceptions
import os
import argparse
import traceback
import ffmpy


def ensure_length(sound: AudioSegment, length: int) -> AudioSegment:
    """Takes a given sound and slows/speeds up its duration to length milliseconds
    Args:
        :param sound: The sound to be stretched or compressed
        :param length: The final desired duration of the sound in milliseconds
    Returns:
        :return modified_sound:
    """
    original_length = len(sound)
    factor = float(original_length/length)

    if factor > 2:
        factor = 2
    if factor < 0.5:
        factor = 0.5

    if factor:
        sound.export('temp0.wav', format='wav')
        ff = ffmpy.FFmpeg(inputs={"temp0.wav": None},
                          outputs={"changed.wav": ["-loglevel", "panic", "-hide_banner", "-nostats", "-filter:a", "atempo=" + str(factor), "-y"]})
        ff.run()
        modified_sound = AudioSegment.from_wav('changed.wav')
        return modified_sound
    return sound


def segment_audio(audio_file, start, end, pre_padding=0.0, post_padding=0.0) -> AudioSegment:
    """ Takes and audio file and returns the segment between start time and end time with some padding
    Args:
        :param audio_file:(str) Name of the audio file to segment
        :param start:(int) The start time of the segment in ms
        :param end:(int) The end time of the segment in ms
        :param pre_padding:(float) The fractional padding to apply towards left
        :param post_padding: (float) Fractional padding to apply towards right
    Returns:
        :return: A split AudioSegment of the audio_file that has been segmented
    """

    audio = AudioSegment.from_wav(audio_file)
    length = end - start

    padded_start = start - length * pre_padding
    padded_end = end + length * post_padding
    segmented_audio = audio[padded_start:padded_end]

    return segmented_audio


def generate_diphones(audio_file, transcript_file, output_folder, pre_padding=0.0, post_padding=0.0) -> set:
    """Generates the list of diphones for a given audio_file using the transcript and store the diphones in the
    output_folder
    Args:
        :param audio_file:(str) Name of the audio file to segment (.wav)
        :param transcript_file:(str) Name of the text file with the transcript
        :param output_folder:(str) Name of the destination directory to store the diphones
        :param pre_padding:(float) A fraction of audio to clip before the generated diphone
        :param post_padding:(float) A fraction of audio to clip after the generated diphone
    Returns:
        :return set of generated diphones
    """
    nthreads = multiprocessing.cpu_count()
    disfluency = False
    conservative = False
    disfluencies = {'uh', 'um'}

    with open(transcript_file, encoding="utf-8") as fh:
        transcript = fh.read()
        print(transcript)
    resources = gentle.Resources()

    with gentle.resampled(audio_file) as wavfile:
        aligner = gentle.ForcedAligner(resources, transcript, nthreads=nthreads, disfluency=disfluency,
                                       conservative=conservative, disfluencies=disfluencies)
        result = aligner.transcribe(wavfile)
        r = json.loads(result.to_json())

    phone_time_list = []
    diphones = set()
    for word in r['words']:
        start = word['start'] * 1000
        for phone in word['phones']:
            diphones.add(phone['phone'])
            phone_time_list.append([phone['phone'], start, start + phone['duration'] * 1000])
            start = start + phone['duration'] * 1000

    for entry in phone_time_list:
        diphone = segment_audio(audio_file, entry[1], entry[2], pre_padding, post_padding)
        print('Old ' + str(entry[0]) + ':' + str(len(diphone)))
        if len(diphone) < 150:
            try:
                diphone = ensure_length(diphone, 150)
            except exceptions.CouldntDecodeError:
                print(entry[0], 'is very small.........................................................')
        if not os.path.exists(output_folder):
            os.mkdir(output_folder)
        output_filename = output_folder + '/' + str(entry[0]) + '.wav'
        diphone.export(output_filename, format='wav')
        print('New ' + str(entry[0]) + ':' + str(len(diphone)))
    return diphones


if __name__ == '__main__':
    """
    To handle if the module is called from command line
    """
    parser = argparse.ArgumentParser(description='Script to produce diphones out of one audio file using the transcript'
                                                 'and store it in the output folder')
    parser.add_argument('audio_file', help='Name of audio file to use')
    parser.add_argument('transcript_file', help='Name of transcript file to use')
    parser.add_argument('output_folder', help='Name of output_folder to store the diphones')
    parser.add_argument('pre_padding', nargs='?', default=0, type=float, help='The pre padding precentage (optional)')
    parser.add_argument('post_padding', nargs='?', default=0, type=float, help='The post padding precentage (optional)')
    args = parser.parse_args()

    audio_file = args.audio_file
    transcript_file = args.transcript_file
    output_folder = args.output_folder
    pre_padding = args.pre_padding
    post_padding = args.post_padding
    print('Aligning', audio_file, 'with', transcript_file)
    diphone_list = None
    try:
        diphone_list = generate_diphones(audio_file, transcript_file, output_folder, pre_padding, post_padding)
    except Exception as E:
        print(E, traceback.print_exc())
    print(diphone_list)
