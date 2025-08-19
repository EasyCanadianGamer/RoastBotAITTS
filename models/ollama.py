import requests
import json

with open("settings.json", "r") as f:
    settings = json.load(f)

# Correct endpoint
OL_API_URL = settings.get("ollamaUrl") or "http://localhost:11434/v1/chat/completions"

def generate_roast(user_message: str, system_message: str = None) -> str:
    """
    Generate a roast using Ollama's local API.
    Uses the chat completions endpoint with messages.
    """
    if system_message is None:
        system_message = "You are a sarcastic AI that roasts users with lots of swearing."

    payload = {
        "model": "Godmoded/llama3-lexi-uncensored:latest",
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ],
        "max_tokens": 150
    }

    headers = {'Content-Type': 'application/json'}

    try:
        # Use json=payload instead of data=json.dumps(payload)
        response = requests.post(OL_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        # The chat API returns the text here:
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("Ollama API error:", e)
        return "Error generating roast"
