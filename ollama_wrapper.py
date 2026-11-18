import os
import json
import time
import requests

def generate_json_response(prompt, model=None, retries=3):
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY is not configured")

    url = "https://api.groq.com/openai/v1/chat/completions"

    payload = {
        "model": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        "messages": [
            {
                "role": "system",
                "content": "Return only a valid JSON object."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "response_format": {"type": "json_object"}
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    for attempt in range(retries):
        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()

            result = response.json()
            response_text = result["choices"][0]["message"]["content"]

            return json.loads(response_text)

        except (requests.exceptions.RequestException,
                json.JSONDecodeError,
                KeyError,
                IndexError) as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(1)

    print("Failed to generate valid JSON.")
    return None
