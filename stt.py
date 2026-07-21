#!/usr/bin/env python3

import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

########################################

from faster_whisper import WhisperModel
from silero_vad import load_silero_vad
import sounddevice as sd
import numpy as np
import torch
import queue
import tts

speech_queue = queue.Queue()

model_size = "distil-medium.en"
model = WhisperModel(model_size, device="cpu", compute_type="int8", cpu_threads=4)
model_vad = load_silero_vad()

samplerate = 16000
CHUNK = 512
THRESHOLD = 0.5
silence = 0
buffer = []
is_speaking = False

def callback( indata, frames, time, status ):
    global is_speaking, buffer, silence, speech_queue, tts_playing

    if tts.tts_playing:
        return

    MAX_SILENCE = 13
    audio_chunk = torch.from_numpy(indata.flatten()).float()
    confidence = model_vad(audio_chunk, samplerate).item()
    #print(confidence)
    if confidence > THRESHOLD:
        if not is_speaking:
           # print("Speech started")
            is_speaking = True
        silence = 0
        buffer.append(indata.flatten().copy())
    else:
        if is_speaking and buffer:
            silence += 1
            if silence >= MAX_SILENCE:
                #print("Speech ended, transcribing...")
                audio = np.concatenate(buffer)
                buffer = []
                is_speaking = False
                segments, info = model.transcribe(
                        audio,
                        language="en",
                        condition_on_previous_text=False,
                        hotwords="Nyra"
                        )
                for segment in segments:
                    speech_queue.put(segment.text)


def stt_start():
    with sd.InputStream(
            samplerate=samplerate,
            channels=1,
            dtype='float32',
            blocksize=CHUNK,
            callback=callback
            ):
        while True:
            sd.sleep(100)
