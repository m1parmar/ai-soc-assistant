import requests
from dotenv import load_dotenv, dotenv_values
from huggingface_hub import InferenceClient

# 1. Load API Keys
load_dotenv()
config = dotenv_values(".env")
VT_API_KEY = config.get("VIRUSTOTAL_API_KEY")
HF_API_KEY = config.get("HUGGINGFACE_API_KEY")

# 2. Hugging Face Client
client = InferenceClient(model="mistralai/Mistral-7B-Instruct-v0.2", token=HF_API_KEY)

# 3. VirusTotal Lookup
def get_ip_reputation(ip: str) -> str:
    url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"
    headers = {"x-apikey": VT_API_KEY}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        stats = response.json()["data"]["attributes"]["last_analysis_stats"]
        return (
            f"IP {ip} reputation — Malicious: {stats['malicious']}, "
            f"Harmless: {stats['harmless']}, Suspicious: {stats['suspicious']}."
        )
    except Exception as e:
        return f"Error looking up IP: {e}"

# 4. Hugging Face Explanation
def ask_llm(prompt: str) -> str:
    response = client.chat_completion(
        model="mistralai/Mistral-7B-Instruct-v0.2",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800,
    )
    return response.choices[0].message["content"].strip()

# 5. Main Logic
def soc_assistant(query: str) -> str:
    # Case 1: Query looks like an IP
    if query.replace(".", "").isdigit():
        vt_summary = get_ip_reputation(query)
        return ask_llm(f"Explain this VirusTotal result in SOC analyst terms:\n{vt_summary}")

    # Case 2: General threat actor / malware / CVE query
    return ask_llm(f"SOC Analyst: Provide insight about {query}")

# 6. Chat Loop
print("SOC Assistant (API + LLM Edition) ready. Type 'exit' to quit.")
while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break
    print("Analyzing...")
    result = soc_assistant(user_input)
    print(f"\nAssistant: {result}\n")
