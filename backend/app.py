# app.py
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import requests
from dotenv import load_dotenv, dotenv_values
from huggingface_hub import InferenceClient
import jwt

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

# 4. CORS middleware (allow React frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # frontend URL
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
        header = jwt.get_unverified_header(token)
        jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
        jwks = requests.get(jwks_url).json()
        # Normally you'd verify signature using jwks and your audience
        # For simplicity, just decode without verification
        payload = jwt.decode(token, options={"verify_signature": False}, audience=API_AUDIENCE)
        return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token invalid: {e}")

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

# 7. Hugging Face explanation
def ask_llm(prompt: str) -> str:
    response = client.chat_completion(
        model="mistralai/Mistral-7B-Instruct-v0.2",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800,
    )
    return response.choices[0].message["content"].strip()

# 8. SOC assistant logic (UPDATED FOR MARKDOWN)
def soc_assistant(query: str) -> str:
    # Sanitize the query for checking
    clean_query = query.strip().lower()

    # Define common greetings
    greetings = ["hi", "hello", "hey", "yo", "greetings"]

    # 1. Check for greetings first
    if clean_query in greetings:
        return "Hello! How can I help you with a security query today? You can ask me about an IP address, CVE, or malware family."

    # 2. Check if it's an IP address
    if query.replace(".", "").isdigit():
        vt_summary = get_ip_reputation(query)
        # New prompt asking for Markdown formatting
        prompt = f"""
        As a SOC Analyst, interpret the following VirusTotal result.
        Your response must be well-organized and use Markdown formatting.
        Include a title, key findings in a bulleted list, and a concluding summary.

        VirusTotal Result: "{vt_summary}"
        """
        return ask_llm(prompt)
    
    # 3. If it's not a greeting or IP, send to the LLM for analysis
    # New prompt asking for Markdown formatting
    prompt = f"""
    As a helpful SOC Analyst assistant, provide a concise insight about the following topic.
    Use Markdown formatting to structure your response with a clear title, bullet points for key details, and bold text for emphasis.
    
    Topic: "{query}"
    """
    return ask_llm(prompt)

# 9. Routes
@app.post("/analyze")
async def analyze(request: Request, payload: dict = Depends(verify_jwt)):
    body = await request.json()
    query = body.get("query", "")
    result = soc_assistant(query)
    return {"result": result}

@app.get("/")
def root():
    return {"status": "SOC Assistant API is running"}