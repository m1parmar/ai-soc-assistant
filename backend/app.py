# app.py
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import requests
from dotenv import load_dotenv, dotenv_values
from huggingface_hub import InferenceClient
import jwt
import asyncio

# 1. Load API keys
load_dotenv()
config = dotenv_values(".env")
VT_API_KEY = config.get("VIRUSTOTAL_API_KEY")
HF_API_KEY = config.get("HUGGINGFACE_API_KEY")
AUTH0_DOMAIN = config.get("AUTH0_DOMAIN")
API_AUDIENCE = config.get("AUTH0_AUDIENCE")

# 2. Hugging Face client
client = InferenceClient(model="mistralai/Mistral-7B-Instruct-v0.2", token=HF_API_KEY)

# 3. FastAPI app
app = FastAPI()

# 4. CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. Auth0 JWT validation
def verify_jwt(request: Request):
    token = request.headers.get("x-token")
    if not token:
        raise HTTPException(status_code=401, detail="Missing x-token header")
    try:
        jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
        requests.get(jwks_url).json()
        payload = jwt.decode(token, options={"verify_signature": False}, audience=API_AUDIENCE)
        return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token invalid: {e}")

# 6. VirusTotal lookup
def get_ip_reputation(ip: str) -> str:
    # ... (This function remains unchanged)
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

# 7. Hugging Face stream generator
async def ask_llm_stream(prompt: str):
    try:
        for token in client.chat_completion(
            model="mistralai/Mistral-7B-Instruct-v0.2",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
            stream=True, # Enable streaming
        ):
            content = token.choices[0].delta.get("content")
            if content:
                yield content
                await asyncio.sleep(0.01) # Small delay for smoother streaming
    except Exception as e:
        print(f"LLM Error: {e}")
        yield "Sorry, there was an error with the AI model."


# 8. Main logic for streaming endpoint
def soc_assistant_stream_logic(query: str):
    clean_query = query.strip().lower()
    greetings = ["hi", "hello", "hey", "yo", "greetings"]

    if clean_query in greetings:
        # For simple greetings, we don't need to stream. Return a generator that yields the full string.
        async def greeting_generator():
            yield "Hello! How can I help you with a security query today?"
        return greeting_generator()

    if query.replace(".", "").isdigit():
        vt_summary = get_ip_reputation(query)
        prompt = f"""
        As a SOC Analyst, interpret the following VirusTotal result. Your response must be well-organized and use Markdown formatting.
        VirusTotal Result: "{vt_summary}"
        """
        return ask_llm_stream(prompt)
    
    prompt = f"""
    As a helpful SOC Analyst assistant, provide a concise insight about the topic. Use Markdown formatting.
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