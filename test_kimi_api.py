import requests
import json

def test_kimi_api():
    api_key = "sk-DPNPWtmRJazhVlC90oR3cNokgrJHhBD4zIqdWfsNdapKh5hg"
    url = "https://api.moonshot.ai/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "moonshot-v1-8k",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello! Can you confirm you are receiving this message?"}
        ],
        "temperature": 0.7
    }
    
    print(f"Testing Kimi AI API at {url}...")
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        print("\nSuccess! Kimi AI responded:")
        print("-" * 20)
        print(content)
        print("-" * 20)
        
    except requests.exceptions.RequestException as e:
        print(f"\nError occurred: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response content: {e.response.text}")

if __name__ == "__main__":
    test_kimi_api()
