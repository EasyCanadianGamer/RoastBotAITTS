# cartesia_ws.py
# Cartesia WebSocket streaming TTS — fully configurable via settings.json

import os
import json
import datetime
import threading
import time
import websocket  # pip install websocket-client
from pydub import AudioSegment
from pydub.playback import play

# Load settings.json
with open("settings.json", "r") as f:
    settings = json.load(f)

# Load Cartesia API key from keys.json
with open("keys.json", "r") as f:
    keys = json.load(f)

CARTESIA_API_KEY = keys.get("cartesia", {}).get("api_key")
if not CARTESIA_API_KEY:
    raise ValueError("Cartesia API key not found in keys.json")

# Cartesia WebSocket endpoint
WS_URL = f"wss://api.cartesia.ai/tts/websocket?api_key={CARTESIA_API_KEY}"

# Get cartesia-ws settings (fallback to cartesia if missing)
ws_settings = settings["tts"].get("cartesia-ws", settings["tts"].get("cartesia", {}))

MODEL_ID = ws_settings.get("model_id", "sonic-3")
VOICE_CONFIG = ws_settings.get("voice", {"mode": "id", "id": "e85bd7a5-08d6-4441-8f65-b09cee0de814"})
LANGUAGE = ws_settings.get("language", "en")
SAMPLE_RATE = ws_settings.get("sample_rate", 24000)  # Optimal for streaming


def speak(
    text: str,
    app_name: str = "roast"
):
    """
    Stream TTS from Cartesia via WebSocket using settings from settings.json.
    Audio plays in real-time with ultra-low latency.
    """
    if not text.strip():
        return

    os.makedirs("roasts", exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    safe_app_name = "".join(c for c in app_name if c.isalnum() or c in (" ", "_", "-")).rstrip()
    filename = f"roasts/{timestamp}_{safe_app_name}.mp3"
    raw_temp = f"roasts/temp_{timestamp}.raw"

    context_id = f"roast-{timestamp}"

    payload = {
        "model_id": MODEL_ID,
        "transcript": text,
        "voice": VOICE_CONFIG,
        "context_id": context_id,
        "language": LANGUAGE,
        "output_format": {
            "container": "raw",
            "encoding": "pcm_f32le",
            "sample_rate": SAMPLE_RATE
        }
    }

    audio_received = threading.Event()

    def on_message(ws, message):
        try:
            data = json.loads(message)
            if data.get("type") == "audio":
                audio_bytes = bytes.fromhex(data["data"])
                with open(raw_temp, "ab") as f:
                    f.write(audio_bytes)
        except Exception as e:
            print(f"[Cartesia WS] Message error: {e}")

    def on_error(ws, error):
        print(f"[Cartesia WS] Error: {error}")

    def on_close(ws, close_status_code, close_msg):
        print(f"[Cartesia WS] Closed: {close_status_code} {close_msg}")

        try:
            if os.path.exists(raw_temp) and os.path.getsize(raw_temp) > 0:
                audio = AudioSegment.from_raw(
                    raw_temp,
                    frame_rate=SAMPLE_RATE,
                    channels=1,
                    sample_width=4  # float32
                )
                audio.export(filename, format="mp3", bitrate="128k")
                print(f"Saved & playing: {filename}")
                play(audio)
            else:
                print("No audio data received.")
        except Exception as e:
            print(f"Playback error: {e}")
        finally:
            if os.path.exists(raw_temp):
                os.remove(raw_temp)
            audio_received.set()

    def on_open(ws):
        print(f"[Cartesia WS] Sending: {text[:50]}...")
        ws.send(json.dumps(payload))

    # Launch WebSocket
    ws = websocket.WebSocketApp(
        WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )

    wst = threading.Thread(target=ws.run_forever, daemon=True)
    wst.start()

    # Wait for completion
    audio_received.wait(timeout=30)

    # Log the text
    log_file = "roasts/roasts.log"
    with open(log_file, "a", encoding="utf-8") as log:
        log.write(f"[{timestamp}] ({app_name}) {text}\n")


