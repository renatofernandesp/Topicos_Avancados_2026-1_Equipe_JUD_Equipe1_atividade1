import os
import httpx
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("LLAMA_API_KEY")
endpoint = os.getenv("LLAMA_ENDPOINT").rstrip("/")
deployment = os.getenv("LLAMA_DEPLOYMENT")

print(f"Testing LLaMa endpoint: {endpoint}")
print(f"Deployment: {deployment}")

def test_endpoint(url, params=None, headers=None):
    if headers is None:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    body = {
        "model": deployment,
        "messages": [{"role": "user", "content": "Respond with the word OK."}],
        "max_tokens": 10
    }
    
    try:
        with httpx.Client(verify=False) as client:
            resp = client.post(url, json=body, headers=headers, params=params, timeout=10)
            print(f"--> URL: {url}")
            print(f"--> Params: {params}")
            print(f"--> Status: {resp.status_code}")
            print(f"--> Response: {resp.text[:200]}")
            print("-" * 50)
            return resp.status_code == 200
    except Exception as e:
        print(f"--> Exception: {e}")
        print("-" * 50)
        return False

# 1. Base /chat/completions (already known to fail with 400 invalid content filter)
test_endpoint(f"{endpoint}/chat/completions")

# 2. Add api-version
test_endpoint(f"{endpoint}/chat/completions", params={"api-version": "2024-05-01-preview"})

# 3. Base /v1/chat/completions
test_endpoint(f"{endpoint}/v1/chat/completions")

# 4. Try without the "models" part if the endpoint has it.
if endpoint.endswith("/models"):
    base_no_models = endpoint[:-7]
    test_endpoint(f"{base_no_models}/openai/deployments/{deployment}/chat/completions", params={"api-version": "2024-05-01-preview"}, headers={"api-key": api_key, "Content-Type": "application/json"})
