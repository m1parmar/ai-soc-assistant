Cybrarian 🛡️
Your AI-Powered SOC Assistant
Cybrarian is a full-stack web application designed to act as an intelligent assistant for Security Operations Center (SOC) analysts. It leverages a large language model and integrates with security APIs to provide instant threat intelligence analysis in a modern, user-friendly chat interface.

Live Demo Link

Features
🤖 AI-Powered Analysis: Get clear, human-readable interpretations of security data from a powerful language model (Mistral-7B).

🌐 Real-time IP Reputation: Instantly check the reputation of any IP address using the VirusTotal API.

🔐 Secure Authentication: User authentication is handled by Auth0, ensuring only authorized personnel can access the tool.

⚡ Streaming Responses: AI responses are streamed token-by-token for a real-time, interactive feel.

🎨 Dual Theme: Includes a sleek, modern interface with both Light and Dark modes.

🚀 Full-Stack Deployment: Deployed with a modern JAMstack architecture, featuring a React frontend on Vercel and a Python backend on Render.

Tech Stack
Frontend
Framework: React

Authentication: Auth0 React SDK

Styling: CSS with Custom Properties for theming

Deployment: Vercel

Backend
Framework: Python with FastAPI

AI: Hugging Face Inference API

Security APIs: VirusTotal

Authentication: PyJWT for token validation

Deployment: Render

Getting Started
Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

Prerequisites
Node.js (v18 or later)

Python (v3.8 or later)

Git

Installation & Setup
Clone the repository:

Bash

git clone https://github.com/your-username/ai-soc-assistant.git
cd ai-soc-assistant
Backend Setup:

Bash

# Navigate to the backend directory
cd backend

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt

# Create a .env file and add your backend secrets (see below)
touch .env
Frontend Setup:

Bash

# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Create a .env file and add your frontend secrets (see below)
touch .env
Environment Variables
You will need to create two .env files and populate them with the following secrets.

backend/.env
VIRUSTOTAL_API_KEY="your_virustotal_api_key"
HUGGINGFACE_API_KEY="your_huggingface_api_key"
AUTH0_DOMAIN="your_auth0_domain"
AUTH0_AUDIENCE="your_auth0_api_audience"
FRONTEND_URL="http://localhost:3000"
frontend/.env
REACT_APP_AUTH0_DOMAIN="your_auth0_domain"
REACT_APP_AUTH0_CLIENT_ID="your_auth0_spa_client_id"
REACT_APP_AUTH0_AUDIENCE="your_auth0_api_audience"
REACT_APP_BACKEND_URL="http://127.0.0.1:8000"
Running the Application Locally
You will need two separate terminals to run both the frontend and backend servers.

Start the Backend Server (from the backend directory):

Bash

# Make sure your virtual environment is activated
uvicorn app:app --reload
The backend will be running at http://127.0.0.1:8000.

Start the Frontend Server (from the frontend directory):

Bash

npm start
The frontend will open in your browser at http://localhost:3000.
