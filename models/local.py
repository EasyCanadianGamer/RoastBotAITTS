import requests
import json

with open("settings.json", "r") as f:
    settings = json.load(f)

OL_API_URL = "http://localhost:11434/api/generate"
def generate_roast(user_message: str, system_message: str = None) -> str:
    """
    Generate a roast using Ollama's local API.
    Combines system and user messages into a single prompt.
    """
    if system_message:
        prompt = f"{system_message}\n\nUser: {user_message}\nAI:"
    else:
        prompt = f"You are a sarcastic AI that roasts users with lots of swearing.\n\nUser: {user_message}\nAI:"

    payload = json.dumps({
          "model": "llama3:latest",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.9,
            "num_predict": 150
        }
    })

    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(OL_API_URL, headers=headers, data=payload)
        response.raise_for_status()
        data = response.json()
        return data["response"].strip()  # <-- use "response" instead of "text"
    except Exception as e:
        print("Ollama API error:", e)
        return "Error generating roast"