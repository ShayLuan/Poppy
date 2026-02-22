# Toolbox
import sys
import os
import json
import ctypes
import time
from vosk import Model, KaldiRecognizer
import pyaudio

# Configuration
MODEL_PATH = "model"
SAMPLE_RATE = 16000

# State variable
is_awake = False    # start the app asleep

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

def open_vscode():
    os.startfile("code.exe")
    print("👨‍💻 Opening VS Code...")

def open_cursor():
    os.startfile("cursor.exe")
    print("👨‍💻 Opening Cursor...")

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
    "open v s code": open_vscode,
    "open cursor": open_cursor,
    "volume up": volume_up,
    "volume down": volume_down,
    "mute": mute_volume,
}

def execute_command(text):
    text = text.lower()

    if "poppy go to sleep" in text or "go to sleep poppy" in text:
        print("😴 Poppy is going to sleep...")
        return "sleep"              # signal

    # check for exit command first
    if "goodbye" in text or "stop listening" in text:
        print("\n👋 Poppy says bye!")
        return False
    
    # loop through command dict
    for keyword, action in COMMANDS.items():
        if keyword in text:
            action()
            return "success"
    print(f"🤔 I heard '{text}', but I don't know that command.")
    return True

def check_wake_phrase(text):
    """
    Only run if Poppy is ASLEEP
    """
    text = text.lower()

    if "hey poppy" in text or "hi poppy" in text or "hello poppy" in text:
        print("⚡ Poppy is awake! Listening...")
        return True
    
    return False

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

print("✅ Poppy is ready! ... but currently asleep.")
print("🗣️ Say 'Hey Poppy' to wake me up.\n")

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

                if not is_awake:
                    if check_wake_phrase(text):
                        is_awake = True
                else:
                    status = execute_command(text)
                    if status == "sleep":
                        is_awake = False

except KeyboardInterrupt:
    print("\n👋 Poppy says bye!")
finally:
    stream.stop_stream()
    stream.close()
    mic.terminate()