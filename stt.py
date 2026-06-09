#!/usr/bin/env python3

from faster_whisper import WhisperModel
from silero_vad import load_silero_vad
import sounddevice as sd
import numpy as np
import torch

model_size = "distil-medium.en"
model = WhisperModel(model_size, device="cpu", compute_type="int8")
model_vad = load_silero_vad()

samplerate = 16000
CHUNK = 512
THRESHOLD = 0.5
silence = 0
buffer = []
is_speaking = False

def callback(indata, frames, t, status):
    global is_speaking, buffer, silence
    MAX_SILENCE = 32
    audio_chunk = torch.from_numpy(indata.flatten()).float()
    confidence = model_vad(audio_chunk, samplerate).item()
    #print(confidence)
    if confidence > THRESHOLD:
        if not is_speaking:
            print("Speech started")
            is_speaking = True
        silence = 0
        buffer.append(indata.flatten().copy())
    else:
        if is_speaking and buffer:
            silence += 1
            if silence >= MAX_SILENCE:
                print("Speech ended, transcribing...")
                audio = np.concatenate(buffer)
                buffer = []
                is_speaking = False
                segments, info = model.transcribe(
                        audio,
                        language="en",
                        condition_on_previous_text=False,
                        hotwords="Nyx"
                        )
                for segment in segments:
                    print("text:", segment.text)

with sd.InputStream(
    samplerate=samplerate,
    channels=1,
    dtype='float32',
    blocksize=CHUNK,
    callback=callback
):
    print("Listening...")
    while True:
        sd.sleep(100)
