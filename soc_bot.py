import os
import requests
from dotenv import load_dotenv
from langchain.agents import tool, AgentExecutor, create_react_agent
from langchain import hub
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.tools.retriever import create_retriever_tool

# --- IMPORTS CHANGED ---
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# 1. Load Environment Variables
load_dotenv()
VT_API_KEY = os.getenv("VIRUSTOTAL_API_KEY")

# 2. Create the Knowledge Base Retriever Tool
loader = DirectoryLoader("./knowledge_base/", glob="**/*.md")
documents = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
texts = text_splitter.split_documents(documents)

# --- EMBEDDINGS CHANGED ---
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

vectorstore = Chroma.from_documents(texts, embeddings)
retriever = vectorstore.as_retriever()

knowledge_base_tool = create_retriever_tool(
    retriever,
    "knowledge_base_search",
    "Searches and returns information from the internal knowledge base, including incident response playbooks and SOPs."
)

# 3. Create a Tool for IP Lookup
@tool
def get_ip_reputation(ip: str) -> str:
    """Looks up an IP address in VirusTotal and returns a summary of its reputation."""
    url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"
    headers = {"x-apikey": VT_API_KEY}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        stats = data['data']['attributes']['last_analysis_stats']
        return f"VirusTotal analysis for {ip}: Malicious: {stats['malicious']}, Harmless: {stats['harmless']}, Suspicious: {stats['suspicious']}."
    except requests.exceptions.RequestException as e:
        return f"Error looking up IP: {e}"

# 4. Initialize the Agent
tools = [knowledge_base_tool, get_ip_reputation]

llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0)

prompt = hub.pull("hwchase17/react")

agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# 5. Run the Chat Loop
print("SOC Assistant (Gemini Edition) is ready. Type 'exit' to quit.")
while True:
    user_input = input("You: ")
    if user_input.lower() == 'exit':
        break
    response = agent_executor.invoke({"input": user_input})
    print(f"Assistant: {response['output']}")