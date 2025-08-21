import requests
import os
import io
from pydub import AudioSegment
from pydub.playback import play
import datetime
import json
from TTS.api import TTS  
import torch
device = "cuda" if torch.cuda.is_available() else "cpu"

# Load keys & settings
with open("keys.json", "r") as f:
    keys = json.load(f)
with open("settings.json", "r") as f:
    settings = json.load(f)

tts_backend = settings.get("TTS_BACKEND", "cartesia")
tts_settings = settings["tts"]

# --- Cartesia setup ---
cartesia_key = keys.get("cartesia", {}).get("api_key")
CARTESIA_URL = "https://api.cartesia.ai/tts/bytes"
CARTESIA_HEADERS = {
    "Cartesia-Version": "2025-04-16",
    "Authorization": f"Bearer {cartesia_key}" if cartesia_key else "",
    "Content-Type": "application/json"
}

def text_to_speech(text, app_name):
    os.makedirs("roasts", exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    safe_app_name = "".join(c for c in app_name if c.isalnum() or c in (" ", "_", "-")).rstrip()
    filename = f"roasts/{timestamp}_{safe_app_name}.mp3"

    if tts_backend == "cartesia":
        # -------------------
        # Cloud Cartesia TTS
        # -------------------
        payload = {
            "model_id": tts_settings["cartesia"]["model_id"],
            "transcript": text,
            "voice": tts_settings["cartesia"]["voice"],
            "output_format": tts_settings["cartesia"]["output_format"],
            "language": tts_settings["cartesia"]["language"]
        }

        response = requests.post(CARTESIA_URL, headers=CARTESIA_HEADERS, json=payload)

        if response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(response.content)
            audio = AudioSegment.from_file(io.BytesIO(response.content), format="mp3")
            play(audio)
        else:
            print("Cartesia error:", response.text)
            return

    elif tts_backend == "coqui":
        # -------------------
        # Local Coqui TTS
        # -------------------
        cfg = tts_settings["coqui"]
        wav_path = filename.replace(".mp3", ".wav")

        # Initialize once (optional: make global for speed)
        tts = TTS(cfg["model"]).to(device)
        tts.tts_to_file(
            text=text,
            file_path=wav_path,
            speaker=cfg.get("speaker", None),
            language=cfg.get("language")
        )

        # Convert to mp3 (optional) + play
        audio = AudioSegment.from_wav(wav_path)
        audio.export(filename, format="mp3")
        play(audio)

    # Log roast text
    log_file = "roasts/roasts.log"
    with open(log_file, "a", encoding="utf-8") as log:
        log.write(f"[{timestamp}] ({app_name}) {text}\n")
    print(f"Logged roast to {log_file}")
