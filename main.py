import json
import os
import time
import pygetwindow as gw
import platform
import subprocess
import text_to_speech
import mc  # our new module
from collections import deque

# -------------------
# Cross-platform notification helper
# -------------------
def notify(title, message):
    if platform.system() == "Darwin":  # macOS
        subprocess.run([
            "osascript",
            "-e",
            f'display notification "{message}" with title "{title}"'
        ])
    else:
        try:
            from plyer import notification
            notification.notify(title=title, message=message, timeout=5)
        except Exception as e:
            print(f"Notification failed: {e}")

# -------------------
# Load settings
# -------------------
with open("settings.json", "r") as f:
    settings = json.load(f)

AI_BACKEND = settings["AI_BACKEND"]
profile_name = settings["profile"]

monitor_mode = settings.get("monitor", {}).get("mode", "window")
minecraft_log_path = settings.get("monitor", {}).get("minecraft_log_path", "")
last_content = ""
last_window = None

# -------------------
# Load profile
# -------------------
profile_path = os.path.join("profiles", profile_name)
with open(profile_path, "r", encoding="utf-8") as f:
    profile = json.load(f)

# -------------------
# Choose AI backend
# -------------------
if AI_BACKEND == "ollama":
    from models import ollama as ai
elif AI_BACKEND == "openai":
    from models import open_AI as ai
elif AI_BACKEND == "local":
    from models import local as ai
else:
    raise ValueError("Invalid AI_BACKEND value in settings.json")

# -------------------
# Build system/user messages
# -------------------
def build_system_message() -> str:
    return (
        f"You are {profile['name']} from {profile['series']}. "
        f"Personality: {profile['personality']}. "
        f"Style: {profile['style']}."
    )

def get_active_window():
    try:
        window = gw.getActiveWindow()
        if window:
            # On macOS, window.title might be a method
            title = window.title() if callable(window.title) else window.title
            return str(title)  # ensure string on all platforms
        return None
    except:
        return None

def get_minecraft_log_tail():
    global last_content
    if not os.path.exists(minecraft_log_path):
        return []

    with open(minecraft_log_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = lines[len(last_content):] if isinstance(last_content, list) else lines
    last_content = lines
    return [line.strip() for line in new_lines if line.strip()]

# -------------------
# Main loop
# -------------------
recent_actions = deque(maxlen=50)  # prevent repeating same roast

while True:
    if monitor_mode == "window":
        target = get_active_window()
        if target and target != last_window:
            last_window = target
            system_message = build_system_message()
            user_message = f"User is currently doing: {target}"
            roast = ai.generate_roast(user_message, system_message=system_message)
            safe_roast = roast[:256]

            notify("AI Roast", safe_roast)
            text_to_speech.text_to_speech(roast, str(target))

    elif monitor_mode == "minecraft":
        new_lines = get_minecraft_log_tail()
        if new_lines:
            action_counts = mc.group_actions(new_lines)

            for action_type, count in action_counts.items():
                if count >= 1 and action_type not in recent_actions:
                    recent_actions.append(action_type)
                    system_message = build_system_message()
                    user_message = f"User performed '{action_type}' {count} times recently."
                    roast = ai.generate_roast(user_message, system_message=system_message)
                    safe_roast = roast[:256]

                    notify("AI Roast", safe_roast)
                    text_to_speech.text_to_speech(roast, str(action_type))

    time.sleep(2)
