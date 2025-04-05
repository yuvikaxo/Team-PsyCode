from vosk import Model, KaldiRecognizer
import pyaudio
import json
import os
from vosk import Model, KaldiRecognizer

model_path = os.path.join(os.getcwd(), "vosk-model-small-en-us-0.15")
model = Model(model_path)
model = Model("model")  # path to the unzipped model folder
recognizer = KaldiRecognizer(model, 16000)

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000,
                input=True, frames_per_buffer=8192)
stream.start_stream()

print("🎤 Speak now...")

while True:
    data = stream.read(4096)
    if recognizer.AcceptWaveform(data):
        result = json.loads(recognizer.Result())
        text = result.get("text", "")
        print("🗣️ You said:", text)
