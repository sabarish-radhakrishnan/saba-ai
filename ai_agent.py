import time
import threading
import requests
import pyautogui
import pyttsx3
import speech_recognition as sr
import sounddevice as sd
import numpy as np
import io
import wave
import queue
import keyboard   # <-- HOTKEY SUPPORT
import base64     # <-- ADDED FOR IMAGE ENCODING

# -----------------------------
# USER STYLE + SYSTEM PROMPT
# -----------------------------

USER_STYLE = """
The user prefers clear, direct, no-fluff explanations.
They like practical, step-by-step answers.
Match that style: be concise, straightforward, and useful.
"""

SYSTEM_PROMPT = f"""
You are the user's personal AI assistant named Saba.

- Respond clearly and directly.
- Avoid unnecessary fluff.
- If something is ambiguous, ask one short follow-up question.
- When explaining, use simple language and practical examples.

User style guide:
{USER_STYLE}
""".strip()

# -----------------------------
# TEXT TO SPEECH ENGINE
# -----------------------------

tts_engine = pyttsx3.init()
tts_queue = queue.Queue()

def tts_worker():
    while True:
        text = tts_queue.get()
        if text is None:
            break
        tts_engine.say(text)
        tts_engine.runAndWait()
        tts_queue.task_done()

tts_thread = threading.Thread(target=tts_worker, daemon=True)
tts_thread.start()

def speak(text):
    tts_queue.put(text)

# -----------------------------
# ASCII BANNER
# -----------------------------

def print_saba_banner():
    banner = r"""
  ____    _     ____     _
 / ___|  / \   | __ )   / \
 \___ \ / _ \  |  _ \  / _ \
  ___) / ___ \ | |_) |/ ___ \
 |____/_/   \_\|____//_/   \_\
"""
    print(banner)

# -----------------------------
# LLaMA MODEL CALLS
# -----------------------------

def _call_llama_model(model_name, messages):
    url = "http://localhost:11434/api/chat"
    payload = {
        "model": model_name,
        "messages": messages,
        "stream": False
    }
    response = requests.post(url, json=payload)
    data = response.json()
    return data["message"]["content"]

def call_fast_model(messages):
    return _call_llama_model("llama3.1", messages)

def call_reasoning_model(messages):
    return _call_llama_model("llama3.1", messages)

def call_coding_model(messages):
    return _call_llama_model("llama3.1", messages)

def call_general_model(messages):
    return _call_llama_model("llama3.1", messages)

# -----------------------------
# ROUTER
# -----------------------------

def route_to_model(user_input):
    text = user_input.lower()

    if any(k in text for k in ["code", "python", "bug", "function", "error"]):
        return "coding"

    if any(k in text for k in ["why", "how does", "explain", "theory", "concept"]):
        return "reasoning"

    if any(k in text for k in ["summarize", "tl;dr", "short version", "brief"]):
        return "fast"

    return "general"

def ask_model(model_name, conversation):
    if model_name == "fast":
        return call_fast_model(conversation)
    elif model_name == "reasoning":
        return call_reasoning_model(conversation)
    elif model_name == "coding":
        return call_coding_model(conversation)
    else:
        return call_general_model(conversation)

# -----------------------------
# SCREEN CONTROL TOOLS
# -----------------------------

def tool_move_and_click(x, y):
    pyautogui.moveTo(x, y, duration=0.5)
    pyautogui.click()

def tool_type_text(text):
    pyautogui.write(text, interval=0.02)

def tool_scroll(amount):
    pyautogui.scroll(amount)

def tool_safe_demo_action():
    x, y = pyautogui.position()
    pyautogui.moveTo(x + 50, y, duration=0.3)
    pyautogui.moveTo(x, y, duration=0.3)

# -----------------------------
# OPEN APPLICATION
# -----------------------------

def open_application(app_name):
    pyautogui.press("win")
    time.sleep(0.3)
    pyautogui.write(app_name)
    time.sleep(0.3)
    pyautogui.press("enter")

# -----------------------------
# SCREEN VISION FUNCTIONS
# -----------------------------

def capture_screen():
    screenshot = pyautogui.screenshot()
    buffer = io.BytesIO()
    screenshot.save(buffer, format="PNG")
    return buffer.getvalue()

def analyze_screen(image_bytes, prompt="Describe what you see on my screen."):
    try:
        # Encode raw bytes → base64 string so JSON can carry it
        encoded_image = base64.b64encode(image_bytes).decode("utf-8")

        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "llama3.2-vision",
                "messages": [
                    {"role": "user", "content": prompt},
                    {"role": "user", "images": [encoded_image]}
                ],
                "stream": False
            },
            timeout=60
        )
        data = response.json()
        return data["message"]["content"]
    except Exception as e:
        msg = f"I had an issue analyzing the screen: {e}"
        speak(msg)
        return msg

def saba_look(prompt="Describe what you see on my screen."):
    img = capture_screen()
    result = analyze_screen(img, prompt)
    print("Saba:", result)
    speak(result)
    return result

# -----------------------------
# SABA LAUNCH BEHAVIOR
# -----------------------------

def launch_saba_behavior():
    speak("Hello Sabarish, I am Saba, your AI assistant.")
    return "Launching Saba... Hello Sabarish."

# -----------------------------
# SLASH COMMANDS
# -----------------------------

voice_mode = False
voice_thread = None

def handle_command(command):
    global voice_mode, voice_thread

    if command == "/demo":
        tool_safe_demo_action()
        return "Demo action executed."

    elif command == "/talk":
        return launch_saba_behavior()

    elif command.startswith("/open"):
        app_name = command.replace("/open", "").strip()
        if not app_name:
            return "Please specify an app to open."
        open_application(app_name)
        return f"Opening {app_name}..."

    elif command == "/look":
        return saba_look("Describe what you see on my screen.")

    elif command == "/amma":
        if not voice_mode:
            voice_mode = True
            voice_thread = threading.Thread(target=always_listening_loop, daemon=True)
            voice_thread.start()
            return "Voice mode activated. Saba is now listening."
        else:
            return "Voice mode is already active."

    elif command == "/appa":
        if voice_mode:
            voice_mode = False
            return "Voice mode deactivated. Saba stopped listening."
        else:
            return "Voice mode is already off."

    else:
        return "Unknown command."

# -----------------------------
# NATURAL LANGUAGE ACTIONS
# -----------------------------

def detect_natural_action(text):
    text = text.lower()

    if text.startswith("saba"):
        command = text.replace("saba", "", 1).strip()

        if command.startswith(("open", "launch", "start", "run")):
            parts = command.split(" ", 1)
            if len(parts) > 1:
                app = parts[1]
                open_application(app)
                return f"Opening {app}..."

        if command.startswith("type"):
            content = command.replace("type", "", 1).strip()
            if content:
                tool_type_text(content)
                return f"Typing: {content}"

        if command.startswith("click"):
            tool_move_and_click(960, 540)
            return "Clicking the center."

        if command.startswith("scroll"):
            tool_scroll(-800)
            return "Scrolling down."

        if command.startswith("search"):
            query = command.replace("search", "", 1).strip()
            if query:
                return f"Searching for {query}..."

        if command.startswith("look"):
            return saba_look("Describe what you see on my screen.")

    return None

# -----------------------------
# VOICE CAPTURE
# -----------------------------

def record_audio(duration=4, sample_rate=16000):
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype="int16")
    sd.wait()

    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio.tobytes())

    return buffer.getvalue()

def recognize_speech():
    recognizer = sr.Recognizer()
    try:
        wav_bytes = record_audio()
        audio_data = sr.AudioData(wav_bytes, sample_rate=16000, sample_width=2)
        text = recognizer.recognize_google(audio_data, language="en-US")
        return text
    except Exception:
        return None

# -----------------------------
# ALWAYS LISTENING LOOP
# -----------------------------

def always_listening_loop():
    print("Voice mode ON: Saba is listening...")

    while voice_mode:
        print("\n[Listening...]")
        text = recognize_speech()

        if not text:
            continue

        print(f"[Voice heard]: {text}")

        action_reply = detect_natural_action(text)
        if action_reply:
            print("Saba:", action_reply)
            speak(action_reply)

# -----------------------------
# HOTKEY LOOK (F8)
# -----------------------------

def hotkey_look_loop():
    while True:
        keyboard.wait("f8")
        saba_look("Describe what you see on my screen.")

# -----------------------------
# MAIN CHAT LOOP
# -----------------------------

def main():
    print_saba_banner()
    speak("Hello Sabarish, I am Saba, your AI Asisstant; Saba is now online.")
    print("Saba: Hello Sabarish, I am Saba, your AI Asisstant; Saba is now online.\n")

    print("Your AI assistant Saba is live. Type 'quit' to exit.")
    print("Voice mode is OFF. Use /amma to activate listening.")
    print("Slash commands: /amma, /appa, /demo, /talk, /open <app>, /look\n")

    threading.Thread(target=hotkey_look_loop, daemon=True).start()

    conversation = [{"role": "system", "content": SYSTEM_PROMPT}]
    global voice_mode

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ["quit", "exit"]:
            print("Saba: Goodbye.")
            speak("Goodbye.")
            break

        if user_input.startswith("/"):
            reply = handle_command(user_input)
            print("Saba:", reply)
            continue

        action_reply = detect_natural_action(user_input)
        if action_reply:
            print("Saba:", action_reply)
            speak(action_reply)
            continue

        conversation.append({"role": "user", "content": user_input})
        model_name = route_to_model(user_input)
        reply = ask_model(model_name, conversation)
        conversation.append({"role": "assistant", "content": reply})

        print(f"\n[Model chosen: {model_name}]")
        print("Saba:", reply, "\n")
        speak(reply)

# -----------------------------
# ENTRY POINT
# -----------------------------

if __name__ == "__main__":
    main()
  
