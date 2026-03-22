import json
import ollama

with open("settings.json", "r") as f:
    settings = json.load(f)

OLLAMA_MODEL = settings.get("ollamaModel", "llama3.2:latest")

def generate_roast(user_message: str, system_message: str = None) -> str:
    if system_message is None:
        system_message = "You are a sarcastic AI that roasts users with lots of swearing."

    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            options={"num_predict": 150}
        )
        return response.message.content.strip()
    except Exception as e:
        print("Ollama error:", e)
        return "Error generating roast"
