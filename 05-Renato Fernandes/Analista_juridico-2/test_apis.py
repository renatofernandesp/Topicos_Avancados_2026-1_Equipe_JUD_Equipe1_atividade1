import os
from openai import AzureOpenAI, OpenAI
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = "Você é um assistente."

# Test GPT-5.4 Nano
print("Testing GPT-5.4 Nano...")
nano_client = AzureOpenAI(
    api_key=os.getenv("NANO_API_KEY"),
    azure_endpoint=os.getenv("NANO_ENDPOINT"),
    api_version=os.getenv("NANO_API_VERSION"),
)
try:
    resp = nano_client.chat.completions.create(
        model=os.getenv("NANO_DEPLOYMENT", "gpt-5.4-nano"),
        messages=[{"role": "user", "content": "Ola"}],
        max_completion_tokens=50,
        temperature=0.1
    )
    print("Nano SUCCESS:", resp.choices[0].message.content)
except Exception as e:
    print("Nano ERROR:", e)

# Test Mistral
print("\nTesting Mistral...")
mistral_client = OpenAI(
    api_key=os.getenv("MISTRAL_API_KEY"),
    base_url=os.getenv("MISTRAL_ENDPOINT"),
)
try:
    resp = mistral_client.chat.completions.create(
        model=os.getenv("MISTRAL_DEPLOYMENT", "mistral-small-2503"),
        messages=[{"role": "user", "content": "Ola"}],
        max_tokens=50,
        temperature=0.1
    )
    print("Mistral SUCCESS:", resp.choices[0].message.content)
except Exception as e:
    print("Mistral ERROR:", e)

# Let's also try Mistral with AzureOpenAI just in case
print("\nTesting Mistral with AzureOpenAI...")
try:
    mistral_az = AzureOpenAI(
        api_key=os.getenv("MISTRAL_API_KEY"),
        azure_endpoint="https://renat-mju7tzz0-eastus2.services.ai.azure.com/models",
        api_version="2024-05-01-preview"
    )
    resp = mistral_az.chat.completions.create(
        model="mistral-small-2503",
        messages=[{"role": "user", "content": "Ola"}],
        max_tokens=50,
        temperature=0.1
    )
    print("Mistral AzureOpenAI SUCCESS:", resp.choices[0].message.content)
except Exception as e:
    print("Mistral AzureOpenAI ERROR:", e)
