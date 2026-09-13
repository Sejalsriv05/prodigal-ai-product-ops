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

# --- Example Usage ---
if __name__ == "__main__":
    # A strict prompt telling the model exactly what keys to generate.
    # We use a 3D animation brief here as a test scenario for your Creative Agent.
    test_prompt = """
    You are a Creative Director. Output a JSON object for a creative visual brief.
    The JSON must contain exactly two keys: "asset_type" and "visual_prompt".
    Example of expected format: {"asset_type": "3D Animation", "visual_prompt": "Cinematic lighting, high resolution, dynamic camera angle..."}
    """
    
    print("Sending request to Ollama...")
    # NOTE: Ensure you have pulled the model first (e.g., by running `ollama run llama3` in your terminal)
    output = generate_json_response(test_prompt, model="llama3")
    
    if output:
        print("\nSuccessfully generated and parsed JSON:")
        print(json.dumps(output, indent=2))