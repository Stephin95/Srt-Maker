#!/usr/bin/env python3

from vosk import Model, KaldiRecognizer, SetLogLevel
import sys
import os
import wave
import subprocess
import srt
import json
import datetime

SetLogLevel(-1)

if not os.path.exists("model"):
    print ("Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
    exit (1)

sample_rate=16000
model = Model("model")
rec = KaldiRecognizer(model, sample_rate)
rec.SetWords(True)
print('starting')
if sys.argv[1].endswith('.mp4'):
    print('Input is a mp4 file\nConverting to wav file')
    convert_video = subprocess.Popen(['ffmpeg','-i' ,sys.argv[1], 'output_audio.wav'],
                                stdout=subprocess.PIPE)
    print('conversion completed')
    print('getting converted wav file for processing')
    process = subprocess.Popen(['ffmpeg', '-loglevel', 'quiet', '-i',
                            'output_audio.wav',
                            '-ar', str(sample_rate) , '-ac', '1', '-f', 's16le', '-'],
                            stdout=subprocess.PIPE)
    print('got wav file for processing')
    

elif sys.argv[1].endswith('.wav'):
    print('Input is a wav file\nstarted processing')
    process = subprocess.Popen(['ffmpeg', '-loglevel', 'quiet', '-i',
                                sys.argv[1],
                                '-ar', str(sample_rate) , '-ac', '1', '-f', 's16le', '-'],
                                stdout=subprocess.PIPE)



WORDS_PER_LINE = 7

def transcribe():
    results = []
    subs = []
    while True:
       data = process.stdout.read(4000)
       if len(data) == 0:
           print('data has no bytes')
           break
       if rec.AcceptWaveform(data):
           res=rec.Result()
        #    print(res['result'][-1]['end'])  
           print(type(res))
           results.append(res)
        #    results.append(rec.Result())
         
    results.append(rec.FinalResult())
    print('started creating srt data')
    for i, res in enumerate(results):
       jres = json.loads(res)
       if not 'result' in jres:
           continue
       words = jres['result']
       for j in range(0, len(words), WORDS_PER_LINE):
           line = words[j : j + WORDS_PER_LINE] 
           s = srt.Subtitle(index=len(subs), 
                   content=" ".join([l['word'] for l in line]),
                   start=datetime.timedelta(seconds=line[0]['start']), 
                   end=datetime.timedelta(seconds=line[-1]['end']))
           subs.append(s)
           print(s)
    return subs
srt_data=srt.compose(transcribe())
print('saving srt data')
f = open("subtitles.srt", "w")
f.write(srt_data)
f.close()
print(srt_data)
print('saving done')
