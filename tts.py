import sounddevice as sd
import threading
from kokoro import KPipeline
from shared import INTENTS, tts_playing

# sd is for audio playback output.

pipeline = KPipeline(lang_code='a', repo_id='hexgrad/Kokoro-82M', device='cuda')

def tts_warmup():
    for _, _, audio in pipeline("warm up", voice='af_bella'):
        pass
#print("Ready.\n")
    # Here, the pipeline object gets created.
    # The Kokoro 82M model weights get loaded in the VRAM (GPU) since device as cuda was specified and, lang_code='a' sets American phonemizer.
    #to match the voice model I used. (can be american or british, etc.).

##################################################################

# This loop is for first time lazy CUDA initialization and possible kernel compilation.
# So this loop iterate the values and, 'pass' here is just for python's syntax requirement - we don't need to do anything with the output (because we just want to warm up first so that the next response will have lower latency.)

###################################################################

def tts_worker(q1):

    while True:
        text = q1.get()
        if text == None:
            break
        print("message get...")
        
        #for intent in intents:
            #if text == intent:
                #break

        generator = pipeline(   
                             text, 
                             voice='af_bella',
                             speed=0.9,
                             split_pattern=r'[.!?]+'
                             )
        # generator object will yield 3 values per chunk on each iteration.
        # gs is for graphemes string (the text chunk being spoken)
        # ps for phoneme representation (pronunciation information)
        # audio -> actual waveform data as numpy array (like audio consists of sampled waveform amplitudes represented as an array)
        for _, _, audio in generator:

            #if not speech_queue.empty():
                #break

            if audio is not None:
                #print(f"Playing: {gs}")
                #print(str(len(audio)/24000) + "s" + " and " + str(len(audio))
                tts_playing = True
                sd.play(audio, 24000)
                sd.wait()
                tts_playing = False
