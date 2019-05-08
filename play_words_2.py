"""
Date : 8-5-19
Description: Module to play sequence of sounds or produce an audio file with those sequence of sounds
"""
from pydub import AudioSegment
import pyaudio
import wave
import argparse
import time


def play_words(source_folder, word_dicts, diphone_silence=.01, word_silence=.2) -> None:
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
            time.sleep(diphone_silence)
        time.sleep(word_silence)


def generate_words_clip(name, source_folder, word_dicts, diphone_silence=10, word_silence=200) -> None:
    """ Generate a wav file of a given sequence of diphones located in source_folder
    Args:
        :param name: (str) Name of the audio file to be generated
        :param source_folder: (str) Location of all the users diphone data
        :param word_dicts: (list) List of dictionaries of form {'word': [array of diphones]}
        :param diphone_silence: (int) Time for silence between each diphone sound in milliseconds
        :param word_silence: (int) Time for silence between each word in milliseconds
    Returns:
        :return: None
    """
    final_sound = AudioSegment.silent(0)
    for word in word_dicts:
        for diphone in list(word.values())[0]:
            diphone_sound_file = source_folder + '/' + diphone + '.wav'
            sound = AudioSegment.from_wav(diphone_sound_file)
            final_sound = final_sound + sound
            final_sound = final_sound + AudioSegment.silent(diphone_silence)
        final_sound = final_sound + word_silence
    final_sound.export(name + '.wav', format='wav')


def output(source_folder, word_list, dict_file,
           diphone_silence=.01, word_silence=.2,
           generate_file=False, name=None) -> list:
    """ Play/Create audio of the words in word_list
    Args:
        :param source_folder: (str) Location of all the users diphone data
        :param word_list: (list) List of words to speak
        :param dict_file: (str) Name of the dictionary file
        :param diphone_silence: (float) Time for silence between each diphone sound in seconds
        :param word_silence: (float) Time for silence between each word in seconds
        :param generate_file: (Boolean) Whether or not the output file has to be mand
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
            continue
    print(word_dicts)
    if generate_file:
        generate_words_clip(name, source_folder, word_dicts, int(diphone_silence*1000), int(word_silence*1000))
    else:
        play_words(source_folder, word_dicts, diphone_silence, word_silence)
    return word_dicts


if __name__ == '__main__':
    """Handling when its called from shell"""
    parser = argparse.ArgumentParser(description='Play audio of sound using generated diphones')
    parser.add_argument('source_folder', help='Location of the diphone audio wavs')
    parser.add_argument('word_list', help='String to be played (text only no punctuation)')
    parser.add_argument('dict_file', help='The dictionary file to be used')
    parser.add_argument('diphone_silence', type=float, help='The silence between every diphone being played')
    parser.add_argument('word_silence', type=float, help='The silence between every word being played')
    parser.add_argument('name', nargs='?', help='The name of the audio file to generate', default=None)
    parser.add_argument('--generate_file', help='Generate an output file. To be used whenever name is given',
                        action='store_true', default=False)
    args = parser.parse_args()

    source_folder = args.source_folder
    word_list = args.word_list.split(' ')
    dict_file = args.dict_file
    diphone_silence = args.diphone_silence
    word_silence = args.word_silence
    name = args.name
    if not args.generate_file and name is not None:
        print('Please use --generate_file flag')
        exit(1)
    if args.generate_file and name is None:
        print('Please enter a file name')
        exit(1)

    output(source_folder, word_list, dict_file, diphone_silence, word_silence, args.generate_file, name)
