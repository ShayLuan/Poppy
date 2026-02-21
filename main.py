# Toolbox
import sys
import os
import json
import ctypes
from vosk import Model, KaldiRecognizer
import pyaudio

# Configuration
MODEL_PATH = "model"
SAMPLE_RATE = 16000

# ==============
# VOLUME CONTROL
# ==============

def change_volume(key_code, amount=5):
    """Generic function to tap a volume key multiple times."""
    for _ in range(amount):
        ctypes.windll.user32.keybd_event(key_code, 0, 0, 0)
        ctypes.windll.user32.keybd_event(key_code, 0, 2, 0)

def volume_up():
    change_volume(0xAF) # 0xAF is UP
    print("🔊 Volume Up!")

def volume_down():
    change_volume(0xAE) # 0xAE is DOWN
    print("🔉 Volume Down!")

def mute_volume():
    # VK_VOLUME_MUTE = 0xAD
    ctypes.windll.user32.keybd_event(0xAD, 0, 0, 0)
    ctypes.windll.user32.keybd_event(0xAD, 0, 2, 0)
    print("🔇 Muted!")


# =====================
# APP OPENING FUNCTIONS
# =====================

def open_notepad():
    os.startfile("notepad.exe")
    print("📝 Opening Notepad...")

def open_calculator():
    os.startfile("calc.exe")
    print("🧮 Opening Calculator...")

def open_brave():
    try:
        os.startfile("brave.exe")
        print("🌐 Opening Brave...")
    except:
        print("❌ Brave not found in path.")

# ============
# COMMAND DICT
# ============
COMMANDS = {
    "open notepad": open_notepad,
    "open calculator": open_calculator,
    "open brave": open_brave,
    "volume up": volume_up,
    "volume down": volume_down,
    "mute": mute_volume,
}

def execute_command(text):
    text = text.lower()

    # check for exit command first
    if "goodbye" in text or "stop listening" in text:
        print("\n👋 Poppy says bye!")
        return False
    
    # loop through command dict
    for keyword, action in COMMANDS.items():
        if keyword in text:
            action()
            return True
    print(f"🤔 I heard '{text}', but I don't know that command.")
    return True

# ==========
# MAIN SETUP
# ==========

print("🧠 Loading model...")
if not os.path.exists(MODEL_PATH):
    print("❌ ERROR: 'model' folder not found!")
    sys.exit(1)

model = Model(lang="en-us", model_path=MODEL_PATH)
recognizer = KaldiRecognizer(model, SAMPLE_RATE)

print("🎤 Opening microphone...")
mic = pyaudio.PyAudio()
stream = mic.open(format=pyaudio.paInt16,
                  channels=1, 
                  rate=SAMPLE_RATE,
                  input=True,
                  frames_per_buffer=8000)

stream.start_stream()

print("✅ Poppy is listening...")
print("(Say 'Goodbye' to stop)\n")

# MAIN LISTENING LOOP
try:
    while True:
        data = stream.read(4000, exception_on_overflow=False)

        if recognizer.AcceptWaveform(data):
            result = recognizer.Result()
            data_json = json.loads(result)          # json.loads returns a dict
            text = data_json["text"]                # access dict elements

            if text:
                print(f"🗣️ You said: {text}")

                # pass the text to command
                keep_running = execute_command(text)
                if not keep_running:
                    break

except KeyboardInterrupt:
    print("\n👋 Poppy says bye!")
finally:
    stream.stop_stream()
    stream.close()
    mic.terminate()