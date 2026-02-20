import sys
import os
import json
from vosk import Model, KaldiRecognizer
import pyaudio

# 1. Load the model here
print("🧠 Loading model...")
if not os.path.exists("model"):               # current directory
    print("❌ ERROR: 'model' folder not found!")
    sys.exit(1)

model = Model(lang="en-us", model_path="model")
recognizer = KaldiRecognizer(model, 16000)
print("✅ Model loaded!")

# 2. Open microphone
print("🎤 Opening Microphone... ")
mic = pyaudio.PyAudio()
stream = mic.open(format=pyaudio.paInt16,
                  channels=1,
                  rate=16000,
                  input=True,
                  frames_per_buffer=8000)
stream.start_stream()
print("✅🎤 Microphone ready! Say something...")
print("(Press Ctrl+C to stop)\n")

# 3. The listen loop
try:
    while True:
        data = stream.read(4000, exception_on_overflow=False)

        if recognizer.AcceptWaveform(data):
            result = recognizer.Result()
            # Use JSON to read the result
            data_json = json.loads(result)
            text = data_json["text"]

            if text:
                print(f"🗣️ You said: {text}")

except KeyboardInterrupt:
    print("\n👋 Stopping...")
    stream.stop_stream()
    stream.close()
    mic.terminate()

