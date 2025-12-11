<img width="2229" height="1197" alt="image" src="https://github.com/user-attachments/assets/98805a4a-91b0-4291-a649-48386b3c001c" />


# 🚀 Multi-Agent Job Screening AI

**Live Demo:**  
https://multi-agent-job-screening-ai-5czmh3wsbombegjvrpw792.streamlit.app/

Multi-Agent Job Screening AI is an intelligent recruitment assistant that automates resume screening, candidate evaluation, and interview communication using a powerful multi-agent architecture.

---

## 🧠 Powered By
- **LangGraph** – Multi-agent orchestration  
- **LLaMA 3.3 (Groq)** – Ultra-fast inference  
- **LangChain + RAG** – Structured information extraction  
- **Streamlit** – Modern UI  
- **Gmail App Passwords** – Secure email automation  

---

# 🧩 Features

## 🔍 1. Resume Extraction Agent
Extracts structured information such as:
- Candidate Name  
- Contact Information  
- Skills  
- Experience, Projects  

---

## 📋 2. Job Description Agent
Parses:
- Required Skills  
- Responsibilities  
- Qualifications  
- Role Expectations  

---

## 🚩 3. Red-Flag Detection Agent
Identifies:
- Job Hopping  
- Employment Gaps  
- Missing Education  
- Skill Mismatch  
- Poor Formatting / Grammar  

---

## 🧑‍💼 4. Recruiter Evaluation Agent
Scores resume vs JD using:
- **Skills Match – 30 pts**  
- **Experience Match – 50 pts**  
- **Education – 10 pts**  
- **Extras (Certifications/Projects) – 10 pts**

Generates:
- Match Score (/100)  
- Skill & Experience Breakdown  
- Final Recommendation: *Hire / Maybe / Reject*  

---

## ✉️ 5. Automated Interview Emails
HR users can input:
- Sender Email  
- Gmail App Password  
- Candidate Email  

System sends:
- Automatically drafted professional interview email  

---

## 🎨 6. Modern Streamlit UI
Includes:
- Sidebar Controls  
- Drag-and-Drop Uploads  
- Tabs: Overview, Agents, Workflow, Output  
- Mermaid Workflow Graph  
- Clean Dark Theme  

---

# 🛠️ Tech Stack

| Component | Technology |
|----------|------------|
| Multi-Agent Framework | LangGraph |
| LLM Backend | Groq API (LLaMA 3.3 70B) |
| UI | Streamlit |
| Extraction | LangChain, PyPDFLoader |
| Email | smtplib (Gmail App Passwords) |
| Visualization | Mermaid Graph |

---

# 📦 Installation

### 1️⃣ Clone the Repository
```sh
git clone https://github.com/GargiGogulwar/multi-agent-job-screening-ai.git
cd multi-agent-job-screening-ai
```
### 2️⃣ Create a Virtual Environment
```
python -m venv .venv
.venv\Scripts\activate
```
### 3️⃣ Install Dependencies
```
pip install -r requirements.txt
```
### 4️⃣ Set Environment Variables (PowerShell)
```
$env:GROQ_API_KEY = "your_groq_api_key_here"
```
### 5️⃣ Run the Application
```
python -m streamlit run app.py
```

## 🖥️ Usage Guide
-Step 1 — Upload Resume (PDF)

-Step 2 — Upload or Paste Job Description

-Step 3 — Enter HR Email Credentials (Optional)

Sender Email

App Password

Candidate Email

-Step 4 — Run Multi-Agent Screening

## Outputs include:

-Extracted Resume Data

-JD Parsing

-Red Flags

-Evaluation Scores

-Auto-Email Option

## 📧 Email Automation (Gmail)

-Uses Gmail App Passwords, not regular login.

-Steps to generate:

-Enable 2FA

-Visit: https://myaccount.google.com/apppasswords

-Create App Password

-Enter it in Streamlit UI

