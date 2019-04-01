import logging
import multiprocessing
import json
import gentle
from pydub import AudioSegment


log_level = 'INFO'
logging.getLogger().setLevel(log_level)

nthreads = multiprocessing.cpu_count()
disfluency = False
conservative=False
disfluencies = set(['uh', 'um'])


def on_progress(p):
    for k,v in p.items():
        logging.debug("%s: %s" % (k, v))


file_name = 'dave/she_will_eat_rice_tomorrow'

with open(file_name+'.txt', encoding="utf-8") as fh:
    transcript = fh.read()

resources = gentle.Resources()
logging.info("converting audio to 8K sampled wav")

with gentle.resampled(file_name+'.wav') as wavfile:
    logging.info("starting alignment")
    aligner = gentle.ForcedAligner(resources, transcript, nthreads=nthreads, disfluency=disfluency, conservative=conservative, disfluencies=disfluencies)
    result = aligner.transcribe(wavfile, progress_cb=on_progress, logging=logging)

r = json.loads(result.to_json())
dur_list = []
phone_list = []

clip = AudioSegment.from_wav(file_name+'.wav')

for word in r['words']:
    dur_list.append([word['alignedWord'],word['start'],word['end']])
    start = word['start']*1000
    for phone in word['phones']:
        phone_list.append([phone['phone'], start, start+phone['duration']*1000])
        start = start + phone['duration']*1000

#print(result.to_json(indent=2))

sample_inc = .001

output_directory = "dave/dave_diphones2/"
for entry in phone_list:
    s = entry[1] - entry[1] * sample_inc
    e = entry[2] + entry[2] * sample_inc
    print(entry[0], s, ':', e)

    clip[s:e].export(output_directory+entry[0]+".wav", format="wav")



