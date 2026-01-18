# app.py (Final Version with Enhanced Logic)
import os
import re # Import the regular expressions module
import json
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import requests
from dotenv import load_dotenv
# from huggingface_hub import InferenceClient  # Commented out - using OpenRouter instead
import jwt
from jwt.algorithms import RSAAlgorithm
import asyncio
import httpx  # For async HTTP requests to OpenRouter

# 1. Load Environment Variables Correctly
load_dotenv()
VT_API_KEY = os.getenv("VIRUSTOTAL_API_KEY")
# HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")  # Commented out - using OpenRouter instead
OPENROUTER_API_KEY = os.getenv("OPENROUTER_KEY")
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
API_AUDIENCE = os.getenv("AUTH0_AUDIENCE")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# 2. OpenRouter configuration
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "xiaomi/mimo-v2-flash:free"

# Old HuggingFace client - commented out for later use
# client = InferenceClient(model="mistralai/Mistral-7B-Instruct-v0.2", token=HF_API_KEY)

# 3. FastAPI app
app = FastAPI()

# 4. CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. Auth0 JWT validation (Secure)
def verify_jwt(request: Request):
    token = request.headers.get("x-token")
    if not token:
        raise HTTPException(status_code=401, detail="Missing x-token header")
    
    try:
        jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
        jwks = requests.get(jwks_url).json()
        
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        if not rsa_key:
            raise HTTPException(status_code=401, detail="Unable to find appropriate key")
            
        public_key = RSAAlgorithm.from_jwk(rsa_key)
        
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=API_AUDIENCE,
            issuer=f"https://{AUTH0_DOMAIN}/"
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token is expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Token invalid: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

# 6. VirusTotal lookup
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

# 7. OpenRouter stream generator
async def ask_llm_stream(prompt: str):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": FRONTEND_URL,
        "X-Title": "Cybrarian SOC Assistant"
    }

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1024,
        "stream": True
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as http_client:
            async with http_client.stream("POST", OPENROUTER_BASE_URL, headers=headers, json=payload) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    print(f"OpenRouter Error: {response.status_code} - {error_text}")
                    yield "Sorry, there was an error with the AI model."
                    return

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]  # Remove "data: " prefix
                        if data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                            content = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue
    except Exception as e:
        print(f"LLM Error: {e}")
        yield "Sorry, there was an error with the AI model."

# Old HuggingFace stream generator - commented out for later use
# async def ask_llm_stream_huggingface(prompt: str):
#     try:
#         for token in client.chat_completion(
#             model="mistralai/Mistral-7B-Instruct-v0.2",
#             messages=[{"role": "user", "content": prompt}],
#             max_tokens=1024,
#             stream=True,
#         ):
#             content = token.choices[0].delta.get("content")
#             if content:
#                 yield content
#                 await asyncio.sleep(0.01)
#     except Exception as e:
#         print(f"LLM Error: {e}")
#         yield "Sorry, there was an error with the AI model."

# 8. Main logic for streaming endpoint (UPGRADED)
def soc_assistant_stream_logic(query: str):
    clean_query = query.strip().lower()
    
    cve_pattern = re.compile(r'cve-\d{4}-\d{4,}', re.IGNORECASE)
    malware_keywords = ['ransomware', 'trojan', 'spyware', 'adware', 'worm', 'rootkit', 'keylogger', 'botnet', 'emotet', 'wannacry', 'ryuk']

    if clean_query in ["hi", "hello", "hey", "yo", "greetings"]:
        async def greeting_generator():
            yield "Hello! I am Cybrarian, your SOC Assistant. How can I help?"
        return greeting_generator()

    cve_match = cve_pattern.search(query)
    if cve_match:
        cve_id = cve_match.group(0).upper()
        prompt = f"""
        As a senior SOC Analyst, provide a detailed summary of the vulnerability {cve_id}.
        Use Markdown formatting. Include the following sections:
        - **CVSS Score & Severity**:
        - **Summary of Vulnerability**:
        - **Impact**:
        - **Affected Software**:
        - **Mitigation/Remediation Steps**:
        """
        return ask_llm_stream(prompt)

    if query.replace(".", "").isdigit():
        vt_summary = get_ip_reputation(query)
        prompt = f"""
        As a SOC Analyst, interpret the following VirusTotal result for the IP address {query}.
        Use Markdown formatting. Include a title, key findings in a bulleted list, and a concluding summary.
        VirusTotal Result: "{vt_summary}"
        """
        return ask_llm_stream(prompt)

    for keyword in malware_keywords:
        if keyword in clean_query:
            prompt = f"""
            As a senior SOC Analyst, explain the malware type: '{keyword.title()}'.
            Use Markdown formatting. Describe its typical behavior, common infection vectors, and key indicators of compromise (IoCs).
            """
            return ask_llm_stream(prompt)

    prompt = f"""
    As a helpful SOC Analyst assistant, provide a concise insight about the following topic.
    Use Markdown formatting to structure your response with a clear title and key details.
    Topic: "{query}"
    """
    return ask_llm_stream(prompt)

# 9. API Routes
@app.post("/stream")
async def stream(request: Request, payload: dict = Depends(verify_jwt)):
    body = await request.json()
    query = body.get("query", "")
    return StreamingResponse(soc_assistant_stream_logic(query), media_type="text/plain")

@app.get("/")
def root():
    return {"status": "SOC Assistant API is running"}