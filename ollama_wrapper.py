import requests
import json
import time

def generate_json_response(prompt, model="llama3", retries=3):
    """
    Sends a prompt to a local Ollama model and forces a JSON response.
    Includes a retry mechanism for malformed outputs.
    """
    url = "http://localhost:11434/api/generate"
    
    # The payload configures the request. 
    # Setting "format": "json" is Ollama's native way to enforce structured output.
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json" 
    }
    
    for attempt in range(retries):
        try:
            # 1. Send the POST request to the local API
            response = requests.post(url, json=payload)
            response.raise_for_status() 
            
            # 2. Extract the text from the response
            result = response.json()
            response_text = result.get("response", "")
            
            # 3. Validate the JSON
            # Even with format="json", smaller local models sometimes hallucinate extra text.
            # json.loads() acts as our strict validator.
            parsed_json = json.loads(response_text)
            
            return parsed_json
            
        except requests.exceptions.RequestException as e:
            print(f"Network error on attempt {attempt + 1}: {e}")
        except json.JSONDecodeError:
            print(f"Malformed JSON output on attempt {attempt + 1}. Retrying...")
        
        # Brief pause before retrying to give the system a breath
        time.sleep(1)
        
    print("Failed to get a valid JSON response after maximum retries.")
    return None

# --- Example Usage (Only runs if you execute this file directly) ---
if __name__ == "__main__":
    test_prompt = """
    You are a Strategist. Output a JSON object with exactly two keys: "target_audience" and "channel_mix".
    Example: {"target_audience": "students", "channel_mix": ["reel", "static"]}
    """
    
    print("Sending request to Ollama...")
    output = generate_json_response(test_prompt, model="llama3")
    
    if output:
        print("\nSuccessfully generated and parsed JSON:")
        print(json.dumps(output, indent=2))