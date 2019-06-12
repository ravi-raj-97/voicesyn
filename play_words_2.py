"""
Date : 8-5-19
Description: Module to play sequence of sounds or produce an audio file with those sequence of sounds
if name is gaven a .wav is generated. otherwise audio is played
"""
from pydub import AudioSegment, playback, effects
import pyaudio
import wave
import argparse
import time


def match_target_amplitude(sound, target_dBFS):
    change_in_dBFS = target_dBFS - sound.dBFS
    return sound.apply_gain(change_in_dBFS)


def overlap(sound_1: AudioSegment, sound_2: AudioSegment, percent: float = .1) -> AudioSegment:
    """Overlap and add some percentage of sound 2 to the back of sound 1
    Args
        :param sound_1: (AudioSegment) The first sound
        :param sound_2: (AudioSegment) The second sound which will be added and overlayed to the first sound
        :param percent: (float) The percentage of the second sound to overlay behind the first audio
    Returns:
        :return overlapped_sound:  AudioSegment
    """

    sound_1_len = len(sound_1)
    sound_2_len = len(sound_2)
    overlap_duration = int(sound_2_len * percent)
    print(sound_1_len, sound_2_len, overlap_duration)
    # overlap_duration = 0 if overlap_duration > sound_1_len else overlap_duration
    # try:
    #     overlapped_sound = sound_1.append(sound_2, crossfade=30)
    # except ValueError:
    #     overlapped_sound = sound_1.append(sound_2, crossfade=0)
    #     return overlapped_sound
    overlapped_sound = sound_1 + AudioSegment.silent(sound_2_len - overlap_duration)
    # playback.play(overlapped_sound)
    overlapped_sound = overlapped_sound.overlay(sound_2, (sound_1_len - overlap_duration), gain_during_overlay=-5)
    return overlapped_sound


def play_words(source_folder, word_dicts, word_silence=.2) -> None:
    """ Play a list of words from a given folder
    Args:
        :param source_folder:(str) Name of folder with the sounds
        :param word_dicts: (list) List of dictionaries of form {'word': [array of diphones]}
        :param diphone_silence: (float) Time for silence between each diphone sound in seconds
        :param word_silence: (float) Time for silence between each word in seconds
    Returns
        :return:(None)
    """
    p = pyaudio.PyAudio()
    chunk = 1024
    for word in word_dicts:
        for diphone in list(word.values())[0]:
            print(diphone)
            audio_file_name = source_folder + '/' + diphone + '.wav'
            wf = wave.open(audio_file_name, 'rb')

            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True)
            data = wf.readframes(chunk)
            while len(data) > 0:
                stream.write(data)
                data = wf.readframes(chunk)
            stream.stop_stream()
            stream.close()
        time.sleep(word_silence)


def generate_words_clip(name, source_folder, word_dicts, word_silence=200) -> None:
    """ Generate a wav file of a given sequence of diphones located in source_folder
    Args:
        :param name: (str) Name of the audio file to be generated
        :param source_folder: (str) Location of all the users diphone data
        :param word_dicts: (list) List of dictionaries of form {'word': [array of diphones]}
        :param word_silence: (int) Time for silence between each word in milliseconds
    Returns:
        :return: None
    """
    final_sound = AudioSegment.silent(0)
    for word in word_dicts:
        diphone_list = list(word.values())[0]
        word_sound = AudioSegment.silent(0)
        for index in range(0, len(diphone_list)):

            diphone = diphone_list[index]
            diphone_sound_file = source_folder + '/' + diphone + '.wav'
            sound = AudioSegment.from_wav(diphone_sound_file)

            if index > 0:
                word_sound = match_target_amplitude(overlap(word_sound, sound), -25)
            else:
                word_sound = match_target_amplitude(word_sound + sound, -25)
        # playback.play(word_sound)
            # final_sound = final_sound + AudioSegment.silent(diphone_silence)
        final_sound = final_sound + word_sound + AudioSegment.silent(word_silence)
    final_sound.export(name + '.wav', format='wav')


def output(source_folder, word_list, dict_file, word_silence=.2, name=None) -> list:
    """ Play/Create audio of the words in word_list
    Args:
        :param source_folder: (str) Location of all the users diphone data
        :param word_list: (list) List of words to speak
        :param dict_file: (str) Name of the dictionary file
        :param word_silence: (float) Time for silence between each word in seconds
        :param name: (str) Name of the output file to be generated
    Returns:
        :return: word_dicts(dict)
    """
    # Read the dictionary
    file = open(dict_file, "r")
    word_dicts = []
    diphone_dict = {}
    for line in file:
        line = line.strip()
        diphone_dict[line.split(" ")[0]] = line.split(" ")[2:]

    # Create a array of {word: [diphones]} objects
    for word in word_list:
        try:
            word_dicts.append({word: diphone_dict[word]})
        except KeyError:
            return {}
    print(word_dicts)
    if name is not None:
        generate_words_clip(name, source_folder, word_dicts, int(word_silence*1000))
    else:
        play_words(source_folder, word_dicts, word_silence)
    print(word_dicts)
    return word_dicts


if __name__ == '__main__':
    """Handling when its called from shell"""
    parser = argparse.ArgumentParser(description='Play audio of sound using generated diphones')
    parser.add_argument('source_folder', help='Location of the diphone audio wavs')
    parser.add_argument('word_list', help='String to be played (text only no punctuation)')
    parser.add_argument('dict_file', help='The dictionary file to be used')
    parser.add_argument('word_silence', type=float, help='The silence between every word being played')
    parser.add_argument('name', nargs='?', help='The name of the audio file to generate (optional)', default=None)
    args = parser.parse_args()

    source_folder = args.source_folder
    word_list = args.word_list.split(' ')
    dict_file = args.dict_file
    word_silence = args.word_silence
    name = args.name

    op = output(source_folder, word_list, dict_file, word_silence, name)
    if len(op) < 1:
        print('word not found')
