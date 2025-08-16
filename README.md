# AI-Powered SOC Assistant 🤖

## Description
A chatbot designed to assist Security Operations Center (SOC) analysts by automating routine tasks like alert enrichment and information retrieval. This project leverages Large Language Models (LLMs) to provide a conversational interface for security tools and internal knowledge bases.

## Features
* **IP Reputation Lookup:** Integrates with the VirusTotal API to check the reputation of IP addresses.
* **Internal Knowledge Base Search:** Uses Retrieval-Augmented Generation (RAG) to answer questions based on internal documents like incident response playbooks.
* (Add more features as you build them!)

## Tech Stack
* **Language:** Python
* **AI/LLM:** Google Gemini, LangChain
* **Vector Database:** ChromaDB
* **APIs:** VirusTotal

## Setup & Installation
1.  Clone the repository:
    `git clone https://github.com/your-username/ai-soc-assistant.git`
2.  Install dependencies:
    `pip install -r requirements.txt`
3.  Create a `.env` file and add your API keys:
    `OPENAI_API_KEY="sk-..."`
    `VIRUSTOTAL_API_KEY="..."`
4.  Run the application:
    `python soc_bot.py`