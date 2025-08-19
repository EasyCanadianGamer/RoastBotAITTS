import requests
import os
import io
from pydub import AudioSegment
from pydub.playback import play
import datetime
import json

# Load Cartesia key from key.json
with open("keys.json", "r") as f:
    keys = json.load(f)
with open("settings.json", "r") as f:
    settings = json.load(f)

tts_settings = settings["tts"]    
cartesia_key = keys["cartesia"]["api_key"]
CARTESIA_URL = "https://api.cartesia.ai/tts/bytes"
CARTESIA_HEADERS = {
    "Cartesia-Version": "2025-04-16",
    "Authorization": f"Bearer {cartesia_key}",
    "Content-Type": "application/json"
}

def text_to_speech(text, app_name):
    # make sure roast directory exists
    os.makedirs("roasts", exist_ok=True)

    # timestamped filename
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    safe_app_name = "".join(c for c in app_name if c.isalnum() or c in (" ", "_", "-")).rstrip()
    filename = f"roasts/{timestamp}_{safe_app_name}.mp3"

    payload = {
    "model_id": tts_settings["model_id"],
        "transcript": text,
        "voice": tts_settings["voice"],
        "output_format": tts_settings["output_format"],
        "language": tts_settings["language"]
    }

    response = requests.post(CARTESIA_URL, headers=CARTESIA_HEADERS, json=payload)

    if response.status_code == 200:
        # save audio file
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"Saved roast to {filename}")

        # play it immediately
        audio = AudioSegment.from_file(io.BytesIO(response.content), format="mp3")
        play(audio)

        # append roast text to log
        log_file = "roasts/roasts.log"
        with open(log_file, "a", encoding="utf-8") as log:
            log.write(f"[{timestamp}] ({app_name}) {text}\n")
        print(f"Logged roast to {log_file}")

    else:
        print("Cartesia error:", response.text)
