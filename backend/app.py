# app.py (Corrected Final Version)
import os
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import requests
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
import jwt
from jwt.algorithms import RSAAlgorithm
import asyncio

# 1. Load Environment Variables Correctly
load_dotenv()
VT_API_KEY = os.getenv("VIRUSTOTAL_API_KEY")
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
API_AUDIENCE = os.getenv("AUTH0_AUDIENCE")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# 2. Hugging Face client
client = InferenceClient(model="mistralai/Mistral-7B-Instruct-v0.2", token=HF_API_KEY)

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

# 5. Auth0 JWT validation (Corrected and Secure)
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

# 6. VirusTotal lookup (Unchanged)
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

# 7. Hugging Face stream generator (Unchanged)
async def ask_llm_stream(prompt: str):
    try:
        for token in client.chat_completion(
            model="mistralai/Mistral-7B-Instruct-v0.2",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
            stream=True,
        ):
            content = token.choices[0].delta.get("content")
            if content:
                yield content
                await asyncio.sleep(0.01)
    except Exception as e:
        print(f"LLM Error: {e}")
        yield "Sorry, there was an error with the AI model."

# 8. Main logic for streaming endpoint (Unchanged)
def soc_assistant_stream_logic(query: str):
    clean_query = query.strip().lower()
    greetings = ["hi", "hello", "hey", "yo", "greetings"]
    if clean_query in greetings:
        async def greeting_generator():
            yield "Hello! How can I help you with a security query today?"
        return greeting_generator()
    if query.replace(".", "").isdigit():
        vt_summary = get_ip_reputation(query)
        prompt = f"""
    You are acting as a SOC Analyst. Investigate and interpret the following IP address: **{query}**.  

    Provide your analysis in a structured report format with the following sections:  

    ## 1. Basic Information  
    - IP Address: {query}  
    - Type: (Public / Private / Reserved / Loopback)  
    - Geolocation (Country, City, ISP, ASN, Organization)  
    - Associated domains (if available)  

    ## 2. Threat Intelligence Sources  
    - VirusTotal Summary: {vt_summary}  
    - Check AbuseIPDB or similar databases for abuse reports.  
    - Mention whether the IP has been seen in:  
    - Spam campaigns  
    - Botnet activity  
    - C2 infrastructure  
    - Scanning activity  

    ## 3. General Security Context  
    - Is the IP in a known hosting provider, cloud service (AWS, Azure, GCP), or residential ISP?  
    - Could this be a proxy / VPN / TOR exit node?  
    - Any indicators it is a false positive (e.g., shared hosting)?  

    ## 4. Potential Impact & Risk  
    - How might this IP interact with an enterprise network? (e.g., inbound scanning, phishing delivery, C2 callbacks)  
    - Risk classification: (Low / Medium / High)  
    - Confidence level: (Low / Medium / High)  

    ## 5. Recommended Actions  
    - Block/allow recommendations (firewall / IDS / EDR).  
    - Monitor for further activity (alerts, logs).  
    - Suggest enrichment steps (reverse DNS, WHOIS lookup, passive DNS).  
    """
        return ask_llm_stream(prompt)

    # fallback if not an IP
    prompt = f"""
    As a helpful SOC Analyst assistant, provide a concise insight about the topic.  
    Use Markdown formatting.  

    **Topic:** {query}
    """
    return ask_llm_stream(prompt)


# 9. API Routes (Unchanged)
@app.post("/stream")
async def stream(request: Request, payload: dict = Depends(verify_jwt)):
    body = await request.json()
    query = body.get("query", "")
    return StreamingResponse(soc_assistant_stream_logic(query), media_type="text/plain")

@app.get("/")
def root():
    return {"status": "SOC Assistant API is running"}