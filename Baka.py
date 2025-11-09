import os
import platform
import datetime
import requests
import psutil
import webbrowser
import urllib.parse

# Try to initialize TTS (pyttsx3). If unavailable, fall back to print-only.
try:
    import pyttsx3
    TTS_AVAILABLE = True
    engine = pyttsx3.init()
    voices = engine.getProperty('voices') or []
except Exception:
    TTS_AVAILABLE = False
    engine = None
    voices = []

current_voice = 'female'

def set_voice(gender='female'):
    """Set the TTS voice if available. This is best-effort and will silently
    fall back to the first available voice or stay print-only if no TTS."""
    global current_voice
    if not TTS_AVAILABLE or not voices:
        current_voice = gender
        return
    # Prefer common Windows voices by name, otherwise use heuristics
    for voice in voices:
        name = getattr(voice, 'name', '') or ''
        if gender.lower() == 'female' and 'zira' in name.lower():
            engine.setProperty('voice', voice.id)
            current_voice = 'female'
            return
        if gender.lower() == 'male' and 'david' in name.lower():
            engine.setProperty('voice', voice.id)
            current_voice = 'male'
            return
    # Fallback: pick the first voice that mentions the gender or the first voice
    for voice in voices:
        name = getattr(voice, 'name', '') or ''
        if gender.lower() in name.lower():
            engine.setProperty('voice', voice.id)
            current_voice = gender
            return
    if voices:
        engine.setProperty('voice', voices[0].id)
        current_voice = gender

set_voice('female')

def speak(text):
    """Speak text with TTS if available, otherwise print. Disables TTS on repeated errors."""
    global TTS_AVAILABLE, engine
    # use ai_name so the printed prefix follows the configured name
    try:
        prefix = ai_name
    except NameError:
        prefix = "BAKA"
    print(f"{prefix}: {text}")
    if TTS_AVAILABLE and engine:
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            # If TTS fails at runtime, disable it to avoid crashes later.
            print(f"[warning] TTS error: {e}. Disabling TTS.")
            TTS_AVAILABLE = False
            engine = None

# System and AI State
ai_name = "BAKA"
version = "v1.6.5"
mode = "offline"

def detect_internet():
    try:
        requests.get("https://www.google.com", timeout=3)
        return True
    except requests.RequestException:
        return False
    except Exception:
        return False

def toggle_mode(command):
    global mode
    if "go online" in command.lower():
        if detect_internet():
            mode = "online"
            speak("Online mode activated.")
        else:
            speak("Internet not available.")
    elif "go offline" in command.lower():
        mode = "offline"
        speak("Offline mode activated.")

def detect_system():
    system_info = {
        "OS": platform.system(),
        "CPU": platform.processor(),
        "RAM": f"{round(psutil.virtual_memory().total / (1024 ** 3))}GB"
    }
    return system_info

def handle_command(command):
    toggle_mode(command)

    if "how are you" in command.lower():
        speak("I'm fully operational.")
    elif "detect hardware" in command.lower():
        info = detect_system()
        speak(f"OS: {info['OS']}, CPU: {info['CPU']}, RAM: {info['RAM']}")
    elif "change voice to female" in command.lower():
        set_voice('female')
        speak("Voice changed to female.")
    elif "change voice to male" in command.lower():
        set_voice('male')
        speak("Voice changed to male.")
    elif "tell me a joke" in command.lower():
        speak("Why don’t scientists trust atoms? Because they make up everything!")
    elif "search" in command.lower() and mode == "online":
        query = command.lower().replace("search", "").strip()
        if not query:
            speak("Please tell me what to search for.")
        else:
            encoded = urllib.parse.quote_plus(query)
            speak(f"Searching for {query} online.")
            webbrowser.open(f"https://www.google.com/search?q={encoded}")
    elif "status" in command.lower():
        speak(f"I am {ai_name} {version}. Current mode is {mode}.")
    else:
        speak(f"You said {command}")

def main():
    speak(f"Hello, I am {ai_name} {version}")
    try:
        while True:
            command = input("You: ")
            if not command:
                continue
            if command.lower() in ["exit", "quit"]:
                speak("Goodbye.")
                break
            if "hey baka" in command.lower():
                speak("Yes?")
                continue
            handle_command(command)
    except KeyboardInterrupt:
        speak("Goodbye.")


if __name__ == "__main__":
    main()