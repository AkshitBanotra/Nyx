import sounddevice as sd
from kokoro import KPipeline


# sd is for audio playback output.

pipeline = KPipeline(lang_code='a', repo_id='hexgrad/Kokoro-82M', device='cuda')
def tts_warmup():
    for _, _, audio in pipeline("warm up", voice='af_bella'):
        pass
#print("Ready.\n")
    # Here, the pipeline object gets created.
    # The Kokoro 82M model weights get loaded in the VRAM (GPU) since device as cuda was specified and, lang_code='b' sets British phonemizer.
    #to match the voice model I used. (since its british :D ).

##################################################################

# This loop is for first time lazy CUDA initialization and possible kernel compilation.
# So this loop iterate the values and, 'pass' here is just for python's syntax requirement - we don't need to do anything with the output (because we just want to warm up first so that the next response will have lower latency.)

###################################################################


def tts_worker(q):
    while True:
        text = q.get()
        if text == None:
            break
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
        for gs, ps, audio in generator:
            if audio is not None:
                #print(f"Playing: {gs}")
                sd.play(audio, 24000) # sd plays the audio data to the playback output of the system! Play audio using Kokoro output sample rate (24KHz).
                # PLayback SR should match generated audio SR.
                # If playback SR is higher -> samples are consumed faster -> shorter duration -> higher pitch.
                # if playback SR is lower -> samples are consumed slower -> longer duration -> lower pitch
                sd.wait() # waits until the full audio gets played by the output stream.



