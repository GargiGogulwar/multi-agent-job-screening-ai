import warnings
warnings.filterwarnings("ignore")

import operator
import os
from typing import Annotated, TypedDict, Sequence

from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph, MessagesState
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage
from langchain_community.document_loaders import PyPDFLoader

# ----------------- ENV & LLM SETUP -----------------

# Load variables from .env if present (optional)
load_dotenv()

# Read Groq API key from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    # Clear error if the key is missing
    raise RuntimeError(
        "GROQ_API_KEY is not set.\n"
        "Set it in PowerShell first, for example:\n"
        '$env:GROQ_API_KEY = "YOUR_GROQ_API_KEY_HERE"'
    )


# Initialize LLM with explicit API key
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=GROQ_API_KEY
)


# TypedDict for AgentState (used by LangGraph)
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]


# ----------------- Resume Name Agent -----------------
def agent(agentState: AgentState):
    """
    Extract candidate name and contact details from Resume.pdf.
    """
    try:
        pdf_file = "Resume.pdf"
        data = PyPDFLoader(pdf_file).load()
        resume_text = " ".join([page.page_content for page in data])

        prompt = (
            "Your task is to extract the candidate name and contact details from the resume data. "
            "Only respond with the candidate name, contact details and nothing else.\n\n"
            f"Resume Data: {resume_text}"
        )

        response = llm.invoke(prompt)
        answer = response.content
    except Exception as ex:
        answer = f"Error extracting name: {ex}"

    return {"messages": [answer]}


# ----------------- Job Description Agent -----------------
def JD_agent(agentState: AgentState):
    """
    Read JD.txt and extract job requirements only.
    """
    try:
        with open("JD.txt", "r", encoding="utf-8") as f:
            jd_data = f.read()

        prompt = (
            "Your task is to extract the exact job requirements from the given data. "
            "Only respond with the job requirements and nothing else.\n\n"
            f"Data: {jd_data}"
        )

        response = llm.invoke(prompt)
        # remove newlines to keep it compact
        result = response.content.replace("\n", " ")
    except Exception as ex:
        result = f"Error extracting job description: {ex}"

    return {"messages": [result]}


# ----------------- Red Flag Detection Agent -----------------
def redflag_agent(agentState: AgentState):
    """
    Analyze resume and list possible red flags for a recruiter.
    """
    try:
        pdf_file = "Resume.pdf"
        data = PyPDFLoader(pdf_file).load()
        resume_text = " ".join([page.page_content for page in data])

        prompt = f"""
You are a Resume Screening Assistant.

Your task is to analyze the candidate's resume and identify any potential **red flags** or **concerns** a recruiter might have.

Look for the following:
- Frequent job switching (e.g., jobs lasting <1 year repeatedly)
- Unexplained employment gaps
- Lack of relevant experience for technical claims
- Missing education details
- Irrelevant experience
- Spelling or grammar issues

Return a list of clear points like:
- "Employment gap between 2020–2022"
- "Mentions Python skills but no project or job experience using it"
- "No education information found"

Resume Data:
{resume_text}
"""

        response = llm.invoke(prompt)
        result = response.content
    except Exception as ex:
        result = f"Error in redflag agent: {ex}"

    return {"messages": [result]}


# ----------------- Recruit Agent (Evaluation) -----------------
def recruit_agent(agentState: AgentState):
    """
    Evaluate how well the resume matches the JD and assign a score out of 100
    with a detailed breakdown and recommendation.
    """
    try:
        pdf_file = "Resume.pdf"
        data = PyPDFLoader(pdf_file).load()
        resume_text = " ".join([page.page_content for page in data])

        messages = agentState["messages"]
        # last 2 messages expected to be JD_agent output and redflag output
        jd_data = str(messages[-2]) + " " + str(messages[-1])

        prompt = f"""
You are a Recruitment AI Assistant.

Your task is to evaluate how well a candidate’s resume matches a given job description
and assign a score out of 100 based on the criteria below.

Scoring Criteria:
- Skills Match: 30 points
- Experience Match: 50 points
    - Do NOT award experience points for roles unrelated to the job description.
    - For freshers:
        - Evaluate based on relevant internships, academic projects, or personal/portfolio work
          that aligns with the job.
    - For experienced candidates:
        - 0–30 pts: Award based on years of relevant experience (e.g., 10 pts per relevant year).
        - 0–20 pts: Award based on quality, relevance, and impact of work.
- Education Match: 10 points
    - If education does NOT match required fields (e.g., CS, DS, AI, or related fields), assign 0.
- Extras (Certifications, Awards, Side Projects): 10 points

Instructions:
- Extract and compare the candidate’s skills, experience, education, and extras to the JD.
- Apply the scoring rules strictly, especially for experience and education.
- Do not award points for irrelevant experience.

After evaluation, return:
1. Total score (out of 100)
2. Score breakdown by category (Skills, Experience, Education, Extras)
3. A short summary (3–4 lines) of strengths and gaps
4. A final recommendation:
    - If score > 75 and key requirements met:
        - "✅ I recommend this candidate for the job."
    - If 50–75:
        - "❌ I do not recommend this candidate for this specific job."
        - "However, I recommend this candidate for an internship or entry-level position..."
    - If < 50:
        - "❌ I do not recommend this candidate for the job." + reason.

Resume Data:
{resume_text}

Job Description (from previous agents):
{jd_data}
"""

        response = llm.invoke(prompt)
        answer = response.content
    except Exception as ex:
        answer = f"Error in recruit agent: {ex}"

    return {"messages": [answer]}
