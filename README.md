SOC Assistant (API + LLM Edition)

SOC Assistant is an advanced, AI-powered security operations chatbot that helps SOC analysts quickly gather intelligence on IP addresses, threat actors, malware, CVEs, and other cybersecurity-related topics. It leverages VirusTotal for IP reputation and Hugging Face’s Mistral-7B-Instruct model to generate human-readable summaries and insights.

Features:
- IP Reputation Lookup: Query any IP address and get a detailed reputation summary from VirusTotal, explained in SOC analyst terms by an AI.
- Threat Actor and Malware Intelligence: Ask about threat actors, malware families, or CVEs, and get summarized insights directly from the AI.
- Conversational Interface: Simple command-line chat loop for easy interaction.
- Extensible: Can be extended to integrate additional threat intelligence APIs or knowledge bases in the future.

Prerequisites:
- Python 3.10 or higher
- API keys:
  - VirusTotal API key
  - Hugging Face API key

Installation:
1. Clone the repository
   git clone https://github.com/yourusername/soc-assistant.git
   cd soc-assistant

2. Create a virtual environment
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows

3. Install dependencies
   pip install requests python-dotenv huggingface-hub

4. Create `.env` file
   VIRUSTOTAL_API_KEY=your_virustotal_api_key
   HUGGINGFACE_API_KEY=your_huggingface_api_key

Usage:
Run the chatbot:
   python soc_assistant.py

Dependencies:
- requests
- python-dotenv
- huggingface-hub

Future Improvements:
- Integrate live threat intelligence APIs (e.g., AlienVault OTX, MITRE ATT&CK) for real-time threat actor insights.
- Add logging and session memory to track ongoing investigations.
- Develop a web-based or GUI interface for SOC analysts.
