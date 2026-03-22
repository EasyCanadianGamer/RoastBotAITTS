import json
import os
import sys
import time
import platform
import subprocess
import text_to_speech
import mc  # our new module
from collections import deque

VERBOSE = "-V" in sys.argv
TEST = "-t" in sys.argv or "--test" in sys.argv

def log(msg):
    if VERBOSE:
        print(f"[DEBUG] {msg}")

# -------------------
# Cross-platform notification helper
# -------------------
def notify(title, message):
    system = platform.system()
    log(f"Sending notification: '{title}' via {system}")
    if system == "Darwin":  # macOS
        subprocess.run([
            "osascript",
            "-e",
            f'display notification "{message}" with title "{title}"'
        ])
    elif system == "Linux":
        try:
            subprocess.run(["notify-send", title, message], check=True)
        except Exception as e:
            print(f"Notification failed: {e}")
    else:  # Windows
        try:
            from plyer import notification
            notification.notify(title=title, message=message, timeout=5)
        except Exception as e:
            print(f"Notification failed: {e}")

# -------------------
# Load settings
# -------------------
log("Loading settings.json")
with open("settings.json", "r") as f:
    settings = json.load(f)

AI_BACKEND = settings["AI_BACKEND"]
profile_name = settings["profile"]

monitor_mode = settings.get("monitor", {}).get("mode", "window")
minecraft_log_path = settings.get("monitor", {}).get("minecraft_log_path", "minecraft")
last_content = ""
last_window = None
user = settings["user"]

log(f"AI backend: {AI_BACKEND}")
log(f"Profile: {profile_name}")
log(f"Monitor mode: {monitor_mode}")
log(f"User: {user}")

# -------------------
# Load profile
# -------------------
profile_path = os.path.join("profiles", profile_name)
log(f"Loading profile from {profile_path}")
with open(profile_path, "r", encoding="utf-8") as f:
    profile = json.load(f)

log(f"Profile loaded: {profile.get('name')} from {profile.get('series')}")

# Choose AI backend
log(f"Importing AI backend: {AI_BACKEND}")
if AI_BACKEND == "ollama":
    from models import ollama as ai
elif AI_BACKEND == "openai":
    from models import open_AI as ai
elif AI_BACKEND == "xai":
    from models import xai as ai
elif AI_BACKEND == "local":
    from models import local as ai
else:
    raise ValueError("Invalid AI_BACKEND value in settings.json")

log("AI backend loaded successfully")

# -------------------
# Test mode
# -------------------
def run_test():
    fake_scenarios = [
        ("window", "YouTube - Watching cat videos at 3am"),
        ("window", "Steam - Among Us"),
        ("window", "Visual Studio Code - main.py"),
        ("minecraft", "mined_dirt"),
        ("minecraft", "died"),
    ]

    print(f"Running test with {len(fake_scenarios)} fake scenarios...\n")
    system_message = build_system_message()

    for mode, target in fake_scenarios:
        print(f"[TEST] Mode: {mode} | Target: {target!r}")
        if mode == "window":
            user_message = f"{user} is currently doing: {target}"
        else:
            user_message = f"{user} performed '{target}' in Minecraft."

        roast = ai.generate_roast(user_message, system_message=system_message)
        print(f"[TEST] Roast: {roast}")
        notify("AI Roast", roast[:256])
        text_to_speech.text_to_speech(roast, target)
        print()

    print("Test complete.")
    sys.exit(0)

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
        system = platform.system()
        if system == "Windows":
            import pygetwindow as gw
            window = gw.getActiveWindow()
            if window:
                title = window.title() if callable(window.title) else window.title
                return str(title)
            return None
        elif system == "Darwin":
            script = 'tell application "System Events" to get name of first application process whose frontmost is true'
            result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
            return result.stdout.strip() or None
        else:  # Linux
            if os.environ.get("WAYLAND_DISPLAY"):
                # Wayland: use lswt
                result = subprocess.run(["lswt", "-j"], capture_output=True, text=True)
                log(f"lswt returncode: {result.returncode} stderr: {result.stderr!r}")
                if result.returncode != 0:
                    log("lswt failed — is it installed? (yay -S lswt)")
                    return None
                data = json.loads(result.stdout)
                if not data.get("supported-data", {}).get("activated"):
                    log("Wayland compositor does not expose activated window state (COSMIC limitation) — cannot detect active window")
                    return None
                for toplevel in data.get("toplevels", []):
                    if toplevel.get("activated"):
                        return toplevel.get("title")
                return None
            else:
                # X11: use xdotool
                result = subprocess.run(["xdotool", "getactivewindow", "getwindowname"], capture_output=True, text=True)
                log(f"xdotool stdout: {result.stdout!r} stderr: {result.stderr!r} returncode: {result.returncode}")
                return result.stdout.strip() or None
    except Exception as e:
        log(f"get_active_window error: {e}")
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
if TEST:
    run_test()

log("Starting main loop")
recent_actions = deque(maxlen=50)  # prevent repeating same roast

while True:
    if monitor_mode == "window":
        target = get_active_window()
        log(f"Active window: {target!r}")
        if target and target != last_window:
            last_window = target
            log(f"Window changed -> generating roast for: {target!r}")
            system_message = build_system_message()
            user_message = f"{user} is currently doing: {target}"
            roast = ai.generate_roast(user_message, system_message=system_message)
            log(f"Roast generated: {roast!r}")
            safe_roast = roast[:256]

            notify("AI Roast", safe_roast)
            log("Playing TTS...")
            text_to_speech.text_to_speech(roast, str(target))
            log("TTS done")

    elif monitor_mode == "minecraft":
        new_lines = get_minecraft_log_tail()
        if new_lines:
            log(f"New Minecraft log lines: {new_lines}")
        action_counts = mc.group_actions(new_lines)

        for action_type, count in action_counts.items():
            if count >= 1 and action_type not in recent_actions:
                recent_actions.append(action_type)
                log(f"Minecraft action: {action_type} x{count} -> generating roast")
                system_message = build_system_message()
                user_message = f"{user} performed '{action_type}' {count} times recently."
                roast = ai.generate_roast(user_message, system_message=system_message)
                log(f"Roast generated: {roast!r}")
                safe_roast = roast[:256]

                notify("AI Roast", safe_roast)
                log("Playing TTS...")
                text_to_speech.text_to_speech(roast, str(action_type))
                log("TTS done")

    time.sleep(2)
