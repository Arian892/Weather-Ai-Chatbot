# voice_input.py
import sounddevice as sd
import queue
import json
from vosk import Model, KaldiRecognizer

q = queue.Queue()
model = Model("model")  # make sure this is the correct model directory
samplerate = 16000

def callback(indata, frames, time, status):
    q.put(bytes(indata))

def record_and_transcribe(duration=5):
    rec = KaldiRecognizer(model, samplerate)
    with sd.RawInputStream(samplerate=samplerate, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        print("Recording...")
        for _ in range(0, int(samplerate / 8000 * duration)):
            data = q.get()
            if rec.AcceptWaveform(data):
                break
        print("Done.")
    result = json.loads(rec.Result())
    return result.get("text", "")
