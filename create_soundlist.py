"""
Date: 7-5-2019
Description: Script to create a list of sounds given a single audio file and the text transcript and store in given directory
"""

import multiprocessing
import json
import gentle
from pydub import AudioSegment
import os
import argparse
import traceback


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
    length = start - end

    padded_start = start - length * pre_padding if start - length * pre_padding > 0 else start
    padded_end = end + length * post_padding if end + length * post_padding < len(audio) else end

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
        if not os.path.exists(output_folder):
            os.mkdir(output_folder)
        output_filename = output_folder + '/' + str(entry[0]) + '.wav'
        diphone.export(output_filename, format='wav')
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
