import pyaudio
import numpy as np

mic = pyaudio.PyAudio()
stream = mic.open(format=pyaudio.paInt16,
                  channels=1,
                  rate=16000,
                  input=True,
                  frames_per_buffer=8000)

print("🎤 Testing microphone levels...")
print("Speak now! (Press Ctrl+C to stop)\n")

try:
    while True:
        data = np.frombuffer(stream.read(8000, exception_on_overflow=False), dtype=np.int16)
        volume = np.abs(data).mean()
        print(f"🔊 Volume level: {volume:.0f}", end='\r')

except KeyboardInterrupt:
    print("\n👋 Stopping...")
    stream.stop_stream()
    stream.close()
    mic.terminate()