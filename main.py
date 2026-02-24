# Toolbox
import sys
import os
import traceback

# Helper function to find paths whether running as script of .exe
def resource_path(relative_path):
    """
    Get absolute path for resource, works for dev and for PyInstaller
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def log_error(error):
    """Write startup/runtime errors to log so they're visible when running with --noconsole."""
    with open("poppy_error.log", "w") as f:
        f.write(f"Error occurred: {str(error)}\n")
        f.write(traceback.format_exc())
    print(f"Error saved to poppy_error.log")

import json
import ctypes
import time
import subprocess

# Defer vosk import until after resource_path is defined (needed for bundled exe)
try:
    from vosk import Model, KaldiRecognizer
except Exception as e:
    if getattr(sys, "frozen", False):
        log_error(e)
    raise
import pyaudio

# Configuration
MODEL_PATH = resource_path("model")
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

# =====================
# APP CLOSING FUNCTIONS
# =====================

def close_notepad():
    try:
        subprocess.run(["taskkill", "/IM", "notepad.exe"],
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL,
                       creationflags=subprocess.CREATE_NO_WINDOW)
        print("📝 Close Notepad...")
    except Exception:
        print("❌ Notepad wasn't open.")

def close_calc():
    try:
        subprocess.run(["taskkill", "/IM", "calc.exe"],
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL,
                       creationflags=subprocess.CREATE_NO_WINDOW)
        print("🧮 Closing Calculator...")
    except Exception:
        print("❌ Calculator wasn't open.")

def close_cursor():
    try:
        subprocess.run(["taskkill", "/IM", "cursor.exe"],
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL,
                       creationflags=subprocess.CREATE_NO_WINDOW)
        print("👨‍💻 Closing Cursor...")
    except Exception:
        print("❌ Cursor wasn't open.")

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
    "close notepad": close_notepad,
    "close calculator": close_calc
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

def main():
    global is_awake
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


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        if getattr(sys, "frozen", False):
            log_error(e)
        raise