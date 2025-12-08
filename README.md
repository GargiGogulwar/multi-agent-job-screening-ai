<img width="2229" height="1197" alt="image" src="https://github.com/user-attachments/assets/98805a4a-91b0-4291-a649-48386b3c001c" />

DEMO OF APP :
https://multi-agent-job-screening-ai-5czmh3wsbombegjvrpw792.streamlit.app/

🚀 Overview

Multi-Agent Job Screening AI is an intelligent recruitment assistant designed to automate the resume screening and candidate evaluation process using:

⚙️ LangGraph for orchestrating multiple intelligent agents

⚡ Llama 3.3 (Groq) for ultra-fast inference

🧠 RAG components for structured extraction

🎨 Streamlit for a clean, interactive UI

✉️ Email automation via Gmail App Passwords

It helps HR teams, companies, and startups:

Quickly evaluate resumes

Detect potential red flags

Score resume–JD similarity

Automatically invite shortlisted candidates for interviews

🧩 Features
🔍 1. Resume Extraction Agent

Extracts:

Candidate name

Contact details

Skills

Experience

📋 2. Job Description Agent

Parses and extracts:

Required skills

Responsibilities

Qualification criteria

🚩 3. Red-Flag Detection Agent

Detects issues like:

Job hopping

Employment gaps

Missing education

No validation for claimed skills

Grammar/formatting issues

🧑‍💼 4. Recruiter Evaluation Agent

Scores resume vs JD using:

Skills Match – 30 pts

Experience Match – 50 pts

Education Match – 10 pts

Extras (Certifications/Projects) – 10 pts

Generates:

Match score (/100)

Detailed breakdown

Recommendation (Hire / Maybe / Reject)

✉️ 5. Automated Interview Emails

HR users can enter:

Their email

Their App Password

Candidate email

The system automatically sends:

A professionally drafted interview email

Directly from the company's own inbox

🎨 6. Modern Streamlit UI

Includes:

Sidebar configuration

Drag-and-drop uploads

Tabs (Overview, Agents, Workflow)

Mermaid workflow graph

Dark + professional theme

🛠️ Tech Stack
Component	Technology
Multi-Agent Framework	LangGraph
LLM Backend	Groq API – LLaMA 3.3 70B
UI Framework	Streamlit
Parsing & Extraction	LangChain, PyPDFLoader
Email Automation	smtplib (Gmail App Password)
Visualization	Mermaid Graph
📦 Installation
1️⃣ Clone the repository
git clone https://github.com/GargiGogulwar/multi-agent-job-screening-ai.git
cd multi-agent-job-screening-ai

2️⃣ Create a virtual environment
python -m venv .venv
.venv\Scripts\activate

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Set your environment variables (PowerShell)
$env:GROQ_API_KEY = "your_groq_api_key_here"


(Email values are entered inside the UI — not here.)

5️⃣ Run the application
python -m streamlit run app.py

🖥️ Usage Guide
▶️ Step 1 — Upload Resume (PDF)
▶️ Step 2 — Upload or paste Job Description
▶️ Step 3 — Enter HR Email Credentials (optional)

Sender email

App Password

Candidate email

▶️ Step 4 — Click Run Multi-Agent Screening

You will then see:

Candidate details

JD data

Red flags

Recruiter evaluation

Score

Auto-email option

📈 Multi-Agent Workflow
Resume Agent ──▶ JD Agent ───────┐
       └─────▶ Red-Flag Agent ──▶ Recruiter Agent ──▶ Evaluation


The application generates a Mermaid workflow graph in real-time.

📧 Email Automation (Gmail)

We use Gmail App Passwords, NOT regular Gmail login.

To generate:

Enable 2FA

Go to: https://myaccount.google.com/apppasswords

Create App Password

Enter it in the Streamlit UI

🔐 Security Notes

No passwords or API keys are stored in the project

Streamlit only holds email/password during the session

GitHub push-protection prevents accidental key uploads

📂 Project Structure
multi-agent-job-screening-ai/
│
├── app.py                 # Streamlit UI + Orchestration
├── multi_agents.py        # All multi-agent logic
├── email_utils.py         # Email sending helper
├── JD.txt                 # JD storage (temporary)
├── Resume.pdf             # Resume storage (temporary)
├── assets/                # Screenshots, diagrams
└── README.md              # Documentation
