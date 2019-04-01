import pyaudio
import wave
import sys
import time
chunk = 1024
p = pyaudio.PyAudio()


diphones_folder = 'dave/dave_diphones2/'


def play_sound(phoneme):
    wf = wave.open(diphones_folder+phoneme+'.wav', 'rb')
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


file = open("split.txt", "r")
dict = {}
for line in file:
    line = line.strip()
    dict[line.split(" ")[0]] = line.split(" ")[2:]

word_list = 'the issue must not be taken to the guy in red'.split(' ')
phoneme_list = []
for word in word_list:
    phoneme_list.append([word, dict[word]])

for entry in phoneme_list:
    print(entry[0], entry[1])
    for sound in entry[1]:
        play_sound(sound)
        #time.sleep(.05)
    time.sleep(.2)
p.terminate()

