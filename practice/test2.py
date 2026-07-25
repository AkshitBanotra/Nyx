#!/usr/bin/env python3

#!/usr/bin/env python3

import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import time
import queue
import threading

import numpy as np
import sounddevice as sd
import torch

from faster_whisper import WhisperModel
from silero_vad import load_silero_vad

# ============================================================
# Whisper
# ============================================================

model = WhisperModel(
    "distil-small.en",
    device="cpu",
    compute_type="int8",
    cpu_threads=4,
)

# ============================================================
# VAD
# ============================================================

vad = load_silero_vad()

# ============================================================
# Audio Settings
# ============================================================

SAMPLE_RATE = 16000
CHUNK = 512

THRESHOLD = 0.5
MAX_SILENCE = 16

# ============================================================
# Runtime
# ============================================================

audio_queue = queue.Queue()

speech_buffer = []

is_speaking = False
silence = 0

# ============================================================
# Whisper Worker
# ============================================================

def stt_worker():

    while True:

        audio = audio_queue.get()

        start = time.perf_counter()

        segments, info = model.transcribe(
            audio,
            language="en",
            condition_on_previous_text=False,
            beam_size=1,
        )

        elapsed = time.perf_counter() - start

        text = ""

        for segment in segments:
            text += segment.text

        text = text.strip()

        if text:

            print("\n----------------------------------------")
            print(f"STT Time : {elapsed:.3f} sec")
            print(f"You      : {text}")
            print("----------------------------------------\n")


# ============================================================
# Audio Callback
# ============================================================

def callback(indata, frames, time_info, status):

    global speech_buffer
    global silence
    global is_speaking

    if status:
        print(status)

    audio_chunk = torch.from_numpy(
        indata.flatten()
    ).float()

    confidence = vad(
        audio_chunk,
        SAMPLE_RATE
    ).item()

    if confidence > THRESHOLD:

        if not is_speaking:

            is_speaking = True
            print("Speech started...")

        silence = 0

        speech_buffer.append(
            indata.flatten().copy()
        )

    else:

        if is_speaking and speech_buffer:

            silence += 1

            if silence >= MAX_SILENCE:

                print("Speech ended.")

                audio = np.concatenate(
                    speech_buffer
                ).copy()

                audio_queue.put(audio)

                speech_buffer.clear()

                silence = 0
                is_speaking = False


# ============================================================
# Main
# ============================================================

def main():

    worker = threading.Thread(
        target=stt_worker,
        daemon=True,
    )

    worker.start()

    print("Listening...\n")

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
        blocksize=CHUNK,
        callback=callback,
    ):

        while True:
            sd.sleep(100)


if __name__ == "__main__":
    main()
