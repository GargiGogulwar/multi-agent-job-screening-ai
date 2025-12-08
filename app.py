import os
import re
import streamlit as st
from multi_agents import *
from langgraph.graph import StateGraph, END
from PIL import Image
from email_utils import send_interview_email


def load_image(image_file):
    return Image.open(image_file)


def extract_score_from_text(text: str) -> int:
    """
    Try to extract a score like '82/100' or 'Score: 82' from the recruiter agent output.
    Returns 0 if not found.
    """
    # Pattern 1: 82/100
    match = re.search(r'(\d+)\s*/\s*100', text)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            pass

    # Pattern 2: Score: 82
    match2 = re.search(r'[Ss]core[^0-9]*(\d+)', text)
    if match2:
        try:
            return int(match2.group(1))
        except ValueError:
            pass

    return 0


def main():
    st.set_page_config(
        page_title="Multi-Agent Job Screening AI",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # ---------------- SIDEBAR ----------------
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")

        st.markdown(
            """
Welcome to **Multi-Agent Job Screening AI** 👋  

Upload a **resume** and a **job description**, and let the agents:

- Extract candidate info  
- Understand the JD  
- Detect red flags  
- Score the candidate  
- Optionally send an **interview invite email**  
            """
        )

        st.markdown("### 🏢 Sender (Company / HR) Email")
        sender_email = st.text_input(
            "Send interview emails FROM this address:",
            placeholder="company.hr@gmail.com",
        )

        sender_password = st.text_input(
            "App Password (NOT normal Gmail password)",
            type="password",
            placeholder="16-character app password from Google",
        )

        st.markdown("### 📨 Candidate Email")
        candidate_email = st.text_input(
            "Send invitation TO this address:",
            placeholder="candidate@example.com",
        )

        threshold = st.slider(
            "✅ Shortlist threshold (Score ≥ x)",
            min_value=0,
            max_value=100,
            value=75,
            step=1,
        )

        st.markdown("---")
        st.markdown(
            "**Tip:** Each HR user can enter *their own* email & app password here.\n\n"
            "No credentials are stored – they are used only for this session."
        )

    # ---------------- HEADER / HERO ----------------
    st.markdown(
        """
    <div style="background-color:#003366;padding:18px;border-radius:10px;margin-bottom:15px;">
        <h1 style="color:white;margin:0;">🧠 Multi-Agent Job Screening Assistant</h1>
        <p style="color:#d9e6ff;margin:5px 0 0;">
            AI-powered resume–JD matching with red-flag detection and recruiter-style evaluation.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # ---------------- MAIN LAYOUT: UPLOAD AREA ----------------
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### 📄 Upload Candidate Resume")
        pdf_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"], key="resume_uploader")
        if pdf_file is not None:
            with open("Resume.pdf", "wb") as f:
                f.write(pdf_file.read())
            st.success("Resume uploaded successfully ✅")

    with col_right:
        st.markdown("### 📋 Job Description")
        text_file = st.file_uploader("Upload Job Description (TXT)", type=["txt"], key="jd_uploader")
        job_description = ""
        if text_file is not None:
            job_description = text_file.read().decode("utf-8", errors="ignore")
        else:
            job_description = st.text_area(
                "Or paste the Job Description here:",
                placeholder="Paste the JD text here...",
                height=180,
            )

        # Save JD to file if provided
        if job_description.strip() != "":
            with open("JD.txt", "w", encoding="utf-8") as f:
                f.write(job_description)

    st.markdown("---")

    # Centered action button
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    with col_btn2:
        run_clicked = st.button("🚀 Run Multi-Agent Screening", use_container_width=True)

    # ---------------- PIPELINE EXECUTION ----------------
    if run_clicked:
        # Basic validation
        if pdf_file is None:
            st.error("⚠️ Please upload a resume PDF before running the screening.")
            return

        if job_description.strip() == "":
            st.error("⚠️ Please upload or paste a Job Description before running the screening.")
            return

        inputs = {
            "messages": [
                "You are a recruitment expert and your role is to match a candidate's profile with a given job description."
            ]
        }

        # Build the workflow
        workflow = StateGraph(AgentState)
        workflow.add_node("Resume_agent", agent)
        workflow.add_node("JD_agent", JD_agent)
        workflow.add_node("Redflag_agent", redflag_agent)
        workflow.add_node("Recruiter_agent", recruit_agent)

        workflow.set_entry_point("Resume_agent")
        workflow.add_edge("Resume_agent", "JD_agent")
        workflow.add_edge("Resume_agent", "Redflag_agent")
        workflow.add_edge("JD_agent", "Recruiter_agent")
        workflow.add_edge("Redflag_agent", "Recruiter_agent")
        workflow.add_edge("Recruiter_agent", END)

        app = workflow.compile()

        with st.spinner("🤖 Running multi-agent evaluation..."):
            # Draw workflow graph once
            img_data = app.get_graph().draw_mermaid_png()
            with open("workflow.png", "wb") as f:
                f.write(img_data)

            outputs = app.stream(inputs)

            # Collect results
            results_by_agent = {
                "Resume_agent": [],
                "JD_agent": [],
                "Redflag_agent": [],
                "Recruiter_agent": [],
            }
            recruiter_raw_text = ""

            for output in outputs:
                for key, value in output.items():
                    messages = value.get("messages", [])
                    for msg in messages:
                        text = str(msg)
                        if key in results_by_agent:
                            results_by_agent[key].append(text)
                        else:
                            results_by_agent[key] = [text]
                        if key == "Recruiter_agent":
                            recruiter_raw_text = text

        st.success("✅ Multi-agent pipeline completed.")

        # --------- TABS FOR RESULTS ----------
        tab_overview, tab_agents, tab_workflow = st.tabs(
            ["📊 Overview & Decision", "🧩 Agent Outputs", "📈 Workflow Graph"]
        )

        # ---- OVERVIEW TAB ----
        with tab_overview:
            st.markdown("### 📊 Overall Evaluation")

            if recruiter_raw_text:
                score = extract_score_from_text(recruiter_raw_text)
                col_o1, col_o2 = st.columns(2)

                with col_o1:
                    st.metric(label="Match Score", value=f"{score} / 100")

                with col_o2:
                    st.metric(label="Shortlist Threshold", value=f"{threshold} / 100")

                if score >= threshold:
                    st.success(f"✅ Candidate is **SHORTLISTED** (Score {score} ≥ {threshold}).")

                    # Email sending logic
                    if candidate_email.strip():
                        if sender_email.strip() and sender_password.strip():
                            st.info("📧 Attempting to send interview invitation email...")
                            email_result = send_interview_email(
                                sender_email.strip(),
                                sender_password.strip(),
                                candidate_email.strip(),
                                "Candidate",
                                score,
                            )
                            if email_result is True:
                                st.success("Email sent successfully! ✅")
                            else:
                                st.error(f"Failed to send email: {email_result}")
                        else:
                            st.error(
                                "Sender email or app password is missing. "
                                "Please fill them in the sidebar to send an email."
                            )
                    else:
                        st.info(
                            "Candidate email is empty. Fill it in the sidebar to send an invite automatically."
                        )
                else:
                    st.warning(f"❌ Candidate is **NOT shortlisted** (Score {score} < {threshold}).")

                st.markdown("#### 📝 Recruiter Summary")
                st.write(recruiter_raw_text)
            else:
                st.warning("Could not read Recruiter agent output to compute the score.")

        # ---- AGENTS TAB ----
        with tab_agents:
            st.markdown("### 🧩 Agent Outputs")

            # Resume Agent
            with st.expander("📄 Resume Agent Output (Candidate Info)", expanded=True):
                if results_by_agent.get("Resume_agent"):
                    for out in results_by_agent["Resume_agent"]:
                        st.write(out)
                else:
                    st.write("No output captured from Resume_agent.")

            # JD Agent
            with st.expander("📋 JD Agent Output (Job Requirements)", expanded=False):
                if results_by_agent.get("JD_agent"):
                    for out in results_by_agent["JD_agent"]:
                        st.write(out)
                else:
                    st.write("No output captured from JD_agent.")

            # Redflag Agent
            with st.expander("🚩 Red Flag Agent Output (Concerns)", expanded=False):
                if results_by_agent.get("Redflag_agent"):
                    for out in results_by_agent["Redflag_agent"]:
                        st.write(out)
                else:
                    st.write("No output captured from Redflag_agent.")

            # Recruiter Agent
            with st.expander("🧑‍💼 Recruiter Agent Output (Detailed Evaluation)", expanded=False):
                if results_by_agent.get("Recruiter_agent"):
                    for out in results_by_agent["Recruiter_agent"]:
                        st.write(out)
                else:
                    st.write("No output captured from Recruiter_agent.")

        # ---- WORKFLOW TAB ----
        with tab_workflow:
            st.markdown("### 📈 Multi-Agent Workflow")
            st.caption("Visual representation of how the agents interact.")
            try:
                st.image(load_image("workflow.png"), caption="Agent Workflow Graph", use_column_width=True)
            except Exception:
                st.warning("Workflow image not available.")


if __name__ == "__main__":
    main()
