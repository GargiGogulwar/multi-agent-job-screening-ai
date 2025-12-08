<img width="2229" height="1197" alt="image" src="https://github.com/user-attachments/assets/98805a4a-91b0-4291-a649-48386b3c001c" />



🧠 Multi-Agent Job Screening AI
AI-powered resume–JD matching with red-flag detection, scoring, and automated interview emails.

🚀 Overview

Multi-Agent Job Screening AI is an intelligent, automated recruitment assistant built using:

LangGraph (multi-agent orchestration)

Llama 3.3 (Groq) ultra-fast inference

RAG components for structured extraction

Streamlit for a clean, interactive UI

Email automation (Gmail App Passwords)

It helps companies quickly evaluate resumes, detect potential issues, compute match scores, and even send interview invitations automatically.

Perfect for HR teams, recruiters, startups, and screening multiple candidates efficiently.

🧩 Features
🔍 1. Resume Extraction Agent

Extracts:

Candidate name

Contact details

Skills

Experience

📋 2. Job Description Agent

Parses the JD and extracts:

Required skills

Responsibilities

Qualification criteria

🚩 3. Red-Flag Detection Agent

Identifies issues such as:

Job hopping

Employment gaps

Missing education

No proof of claimed skills

Grammar or formatting issues

🧑‍💼 4. Recruiter Evaluation Agent

Scores resume vs JD using:

Skills match (30 pts)

Experience match (50 pts)

Education relevance (10 pts)

Extra achievements (10 pts)

Generates:

Match score (/100)

Detailed analysis

Acceptance or rejection recommendation

✉️ 5. Automated Interview Emails

HR users can input:

Their email

Their app password

Candidate's email

And the system sends:

A professional interview invitation

From the company’s own email address

🎨 6. Modern UI

Built with Streamlit featuring:

Sidebar configuration

Drag-and-drop uploads

Tabs (Overview, Agents, Workflow)

Mermaid workflow diagram

🛠️ Tech Stack
Component	Technology
Multi-Agent Framework	LangGraph
LLM Backend	Groq API – LLaMA 3.3 70B Versatile
UI	Streamlit
Extraction	PyPDFLoader, LangChain
Email Automation	smtplib (Gmail App Password)
Workflow Visualization	Mermaid Graph
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


(Email variables are entered inside the app UI — not here.)

5️⃣ Run the application
python -m streamlit run app.py

🖥️ Usage Guide
Step 1 — Upload Resume (PDF)
Step 2 — Upload or Paste Job Description
Step 3 — Configure HR email (Optional)

Sender email

App password

Candidate email

Step 4 — Run Multi-Agent Screening

You will see:

Extracted candidate information

Extracted JD data

Red flags

Recruiter evaluation

Score

Auto-email send option

📈 Multi-Agent Workflow

The app visualizes the following workflow:

Resume Agent ───▶ JD Agent ───┐
         └────▶ Red-Flag Agent ─▶ Recruiter Agent ─▶ Evaluation


A generated Mermaid graph is displayed in the UI.

📧 Email Automation (Gmail)

We use Gmail App Passwords, NOT regular login credentials.
To generate:

Enable 2FA

Go to: https://myaccount.google.com/apppasswords

Create App Password

Use that password in the Streamlit UI

Your app will securely send emails from your own inbox.

🔐 Security Notes

No email passwords or API keys are stored

All sensitive data is session-only via Streamlit inputs

GitHub push-protection prevents accidental key leaks

📂 Project Structure
multi-agent-job-screening-ai/
│
├── app.py                 # Streamlit UI + orchestration
├── multi_agents.py        # All LangGraph agent logic
├── email_utils.py         # Email sending helper
├── JD.txt                 # Temporary JD store
├── Resume.pdf             # Temporary resume storage
├── assets/                # Screenshots, graphs
└── README.md
