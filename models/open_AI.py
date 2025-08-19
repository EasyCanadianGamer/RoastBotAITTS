from openai import OpenAI
import json

# Load OpenAI key from key.json
with open("keys.json", "r") as f:
    keys = json.load(f)

client = OpenAI(api_key=keys["openai"]["api_key"])

def generate_roast(prompt: str, system_message: str = None) -> str:
    if system_message is None:
        system_message = "You are a sarcastic AI that roasts users with lots of swearing."

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
        max_tokens=100
    )
    return response.choices[0].message.content.strip()
