import os
import httpx
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("LLAMA_API_KEY")
endpoint = os.getenv("LLAMA_ENDPOINT")
deployment = os.getenv("LLAMA_DEPLOYMENT", "Llama-4-Maverick-17B-128E-Instruct-FP8")

print("Endpoint:", endpoint)
print("Deployment:", deployment)
print()

url = endpoint.rstrip("/") + "/chat/completions"
headers = {
    "Authorization": "Bearer " + api_key,
    "Content-Type": "application/json",
}
body = {
    "model": deployment,
    "messages": [{"role": "user", "content": "Diga ola"}],
    "max_tokens": 50,
    "temperature": 0.1
}

with httpx.Client(verify=False) as client:
    # Sem api-version
    print("=== Teste 1: Sem api-version ===")
    r = client.post(url, json=body, headers=headers, timeout=30)
    print("Status:", r.status_code)
    print("Resposta:", r.text[:600])
    print()

    # Com api-version
    print("=== Teste 2: api-version=2024-05-01-preview ===")
    r2 = client.post(url, json=body, headers=headers, params={"api-version": "2024-05-01-preview"}, timeout=30)
    print("Status:", r2.status_code)
    print("Resposta:", r2.text[:600])
    print()
