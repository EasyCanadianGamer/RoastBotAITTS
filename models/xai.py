# xai.py
# Grok API integration for RoastBotAITTS
# Keeps default system message, but allows full override via profiles (like Adam.json)

import json
import requests

# Load keys from keys.json
with open("keys.json", "r") as f:
    keys = json.load(f)

XAI_API_KEY = keys["xai"]["api_key"]

BASE_URL = "https://api.x.ai/v1"
ENDPOINT = f"{BASE_URL}/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {XAI_API_KEY}",
    "Content-Type": "application/json"
}

def generate_roast(prompt: str, system_message: str = None) -> str:
    """
    Generate a roast using Grok (xAI API).
    
    Args:
        prompt: The event-based prompt (e.g., "Player died to lava while naked")
        system_message: Optional – full personality profile system prompt.
                        If None, uses a neutral default (sarcastic roaster).
    
    Returns:
        The generated roast text
    """
    # DEFAULT – only used if no profile is passed
    if system_message is None:
        system_message = (
            "You are a sarcastic AI companion that roasts the player in Minecraft. "
            "Be funny, savage, and react to their actions, deaths, builds, and appearance. "
            "Use casual language and light swearing. Keep responses short: 2-4 sentences."
        )

    payload = {
        "model": "grok-4-0709",           # Main Grok model as of 2026
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 150,
        "temperature": 0.9,
        "top_p": 0.95
    }

    try:
        response = requests.post(ENDPOINT, headers=HEADERS, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        roast = data["choices"][0]["message"]["content"].strip()
        return roast

    except requests.exceptions.HTTPError as http_err:
        error_detail = response.text if 'response' in locals() else "No detail"
        print(f"Grok API HTTP error: {http_err} – {error_detail}")
        return "[Grok error – try again later]"
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return "[No connection to Grok]"
    except Exception as e:
        print(f"Unexpected error in xai.py: {e}")
        return "[Adam broke lol]"

# Quick test (run file directly)
# if __name__ == "__main__":
#     # Test with default
#     print("=== Default Personality ===")
#     print(generate_roast("Player just died to a creeper while wearing full leather armor"))

#     # Test with Adam profile override
#     adam_system = (
#         "You are Adam, the player's chaotic Minecraft homeboy. "
#         "You're flirty and freaky with the homie, drop subtle gay panic jokes that stay playful "
#         "(use stuff like 'ayoo', 'pause', 'no homo', 'sus', 'thick'). "
#         "Roast the player hard in 2-4 short, funny sentences. "
#         "Be savage, use swearing, react to their appearance, deaths, builds, etc. "
#         "Keep it bro-energy: toxic but loving."
#     )
#     print("\n=== Adam Personality ===")
#     print(generate_roast("Player just died to a creeper while wearing full leather armor", adam_system))