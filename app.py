import os
import re
import streamlit as st
from multi_agents import *
from langgraph.graph import StateGraph, END
from PIL import Image
from email_utils import send_interview_email
import pandas as pd


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

Upload one or many **resumes** and a **job description**, and let the agents:

- Extract candidate info  
- Understand the JD  
- Detect red flags  
- Score the candidates  
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

        st.markdown("### 📨 Candidate Email (for single-resume mode)")
        candidate_email = st.text_input(
            "Send invitation TO this address (used when only one resume is uploaded):",
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
        st.markdown("### 📄 Batch Email Mapping (Optional)")
        email_mapping_file = st.file_uploader(
            "Upload CSV mapping resumes to candidate emails",
            type=["csv"],
            help="CSV must contain columns: 'resume' and 'email'. 'resume' should match the uploaded file name.",
        )

        st.markdown(
            "**Tip:** Each HR user can enter *their own* email & app password here.\n\n"
            "For multiple resumes, all will be scored. Upload a CSV to enable batch emailing to shortlisted candidates."
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

    # ---- MULTI-RESUME UPLOAD ----
    with col_left:
        st.markdown("### 📄 Upload Candidate Resumes")
        resume_files = st.file_uploader(
            "Upload Resumes (PDF) — you can upload multiple resumes at once",
            type=["pdf"],
            accept_multiple_files=True,
            key="resume_uploader",
        )
        if resume_files:
            st.success(f"{len(resume_files)} resume(s) uploaded successfully ✅")

    # ---- JD UPLOAD / TEXT ----
    with col_right:
        st.markdown("### 📋 Job Description")
        text_file = st.file_uploader(
            "Upload Job Description (TXT)", type=["txt"], key="jd_uploader"
        )
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
        run_clicked = st.button(
            "🚀 Run Multi-Agent Screening for All Resumes", use_container_width=True
        )

    # ---------------- PIPELINE EXECUTION ----------------
    if run_clicked:
        # Basic validation
        if not resume_files:
            st.error("⚠️ Please upload at least one resume (PDF).")
            return

        if job_description.strip() == "":
            st.error("⚠️ Please upload or paste a Job Description.")
            return

        # ----- Build the workflow once -----
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

        app_graph = workflow.compile()

        with st.spinner("🤖 Running multi-agent evaluation for all resumes..."):
            # Draw workflow graph once
            img_data = app_graph.get_graph().draw_mermaid_png()
            with open("workflow.png", "wb") as f:
                f.write(img_data)

            all_results = []  # store results for each resume

            # ----- Process each resume one-by-one -----
            for idx, pdf in enumerate(resume_files, start=1):
                st.markdown(f"### 📄 Processing Resume {idx}: **{pdf.name}**")

                # Save this resume as Resume.pdf (multi_agents.py expects this file)
                with open("Resume.pdf", "wb") as f:
                    f.write(pdf.read())

                # Initial messages into the graph
                inputs = {
                    "messages": [
                        "You are a recruitment expert and your role is to match a candidate's profile with a given job description."
                    ]
                }

                outputs = app_graph.stream(inputs)

                # Collect results for this resume
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

                score = extract_score_from_text(recruiter_raw_text)

                # Store for global summary
                all_results.append(
                    {
                        "file": pdf.name,
                        "score": score,
                        "recruiter_text": recruiter_raw_text,
                        "agents": results_by_agent,
                    }
                )

                st.info(f"Score for **{pdf.name}**: **{score} / 100**")
                st.markdown("---")

        st.success("✅ Multi-agent pipeline completed for all resumes.")

        # --------- TABS FOR RESULTS ----------
        tab_overview, tab_per_resume, tab_workflow = st.tabs(
            ["📊 Overview & Ranking", "🧩 Per-Resume Details", "📈 Workflow Graph"]
        )

        # ---- OVERVIEW TAB ----
        with tab_overview:
            st.markdown("### 📊 Summary of All Resumes")

            if all_results:
                # Build a DataFrame for display
                df_data = []
                for r in all_results:
                    decision = (
                        "SHORTLISTED ✅" if r["score"] >= threshold else "Not Shortlisted ❌"
                    )
                    df_data.append(
                        {
                            "Resume": r["file"],
                            "Score": r["score"],
                            "Decision (Threshold = {})".format(threshold): decision,
                        }
                    )

                df = pd.DataFrame(df_data)
                st.dataframe(df, use_container_width=True)

                # If only one resume -> show detailed view and single-email option
                if len(all_results) == 1:
                    single = all_results[0]
                    score = single["score"]
                    recruiter_text = single["recruiter_text"]

                    st.markdown("### 🧾 Detailed Result (Single Resume Mode)")
                    st.metric("Match Score", f"{score} / 100")
                    st.metric("Shortlist Threshold", f"{threshold} / 100")

                    if score >= threshold:
                        st.success(
                            f"✅ Candidate is **SHORTLISTED** (Score {score} ≥ {threshold})."
                        )

                        # Email sending logic (only if a single resume and email filled)
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
                        st.warning(
                            f"❌ Candidate is **NOT shortlisted** (Score {score} < {threshold})."
                        )

                    st.markdown("#### 📝 Recruiter Summary")
                    st.write(recruiter_text)

                # MULTI-RESUME MODE: enable batch emailing to shortlisted candidates
                else:
                    st.info(
                        "Multiple resumes processed. You can send emails to all shortlisted candidates using the CSV mapping."
                    )

                    st.markdown("### ✉️ Batch Email to Shortlisted Candidates")

                    # Filter shortlisted candidates
                    shortlisted = [r for r in all_results if r["score"] >= threshold]

                    if not shortlisted:
                        st.warning("No candidates met the shortlist threshold.")
                    else:
                        st.write(
                            f"{len(shortlisted)} candidate(s) shortlisted with score ≥ {threshold}."
                        )

                        if email_mapping_file is None:
                            st.info(
                                "To send emails in batch, upload a CSV in the sidebar with columns: 'resume' and 'email'. "
                                "'resume' must match the uploaded PDF file name."
                            )
                        else:
                            try:
                                df_map = pd.read_csv(email_mapping_file)
                            except Exception as e:
                                st.error(f"Could not read CSV file: {e}")
                                df_map = None

                            if df_map is not None:
                                if not {"resume", "email"}.issubset(df_map.columns):
                                    st.error(
                                        "CSV must contain columns named exactly: 'resume' and 'email'."
                                    )
                                else:
                                    if st.button("📧 Send emails to all shortlisted candidates"):
                                        if not sender_email.strip() or not sender_password.strip():
                                            st.error(
                                                "Sender email or app password is missing. Fill them in the sidebar."
                                            )
                                        else:
                                            sent_count = 0
                                            skipped = []

                                            for r in shortlisted:
                                                resume_name = r["file"]
                                                score = r["score"]

                                                row = df_map[df_map["resume"] == resume_name]
                                                if row.empty:
                                                    skipped.append(resume_name)
                                                    continue

                                                to_email = row["email"].values[0]

                                                result = send_interview_email(
                                                    sender_email.strip(),
                                                    sender_password.strip(),
                                                    to_email.strip(),
                                                    "Candidate",
                                                    score,
                                                )

                                                if result is True:
                                                    sent_count += 1
                                                else:
                                                    skipped.append(
                                                        f"{resume_name} (error: {result})"
                                                    )

                                            st.success(
                                                f"✅ Emails sent to {sent_count} shortlisted candidate(s)."
                                            )
                                            if skipped:
                                                st.warning(
                                                    "Some candidates were skipped (missing email mapping or error):\n"
                                                    + "\n".join(f"- {name}" for name in skipped)
                                                )
            else:
                st.warning("No results available to summarize.")

        # ---- PER-RESUME DETAILS TAB ----
        with tab_per_resume:
            st.markdown("### 🧩 Per-Resume Agent Outputs")

            if not all_results:
                st.write("No resume results to display.")
            else:
                for r in all_results:
                    st.markdown(f"#### 📄 {r['file']} — Score: {r['score']} / 100")
                    agents = r["agents"]

                    # Resume Agent
                    with st.expander("📄 Resume Agent Output (Candidate Info)", expanded=False):
                        if agents.get("Resume_agent"):
                            for out in agents["Resume_agent"]:
                                st.write(out)
                        else:
                            st.write("No output captured from Resume_agent.")

                    # JD Agent
                    with st.expander("📋 JD Agent Output (Job Requirements)", expanded=False):
                        if agents.get("JD_agent"):
                            for out in agents["JD_agent"]:
                                st.write(out)
                        else:
                            st.write("No output captured from JD_agent.")

                    # Redflag Agent
                    with st.expander("🚩 Red Flag Agent Output (Concerns)", expanded=False):
                        if agents.get("Redflag_agent"):
                            for out in agents["Redflag_agent"]:
                                st.write(out)
                        else:
                            st.write("No output captured from Redflag_agent.")

                    # Recruiter Agent
                    with st.expander(
                        "🧑‍💼 Recruiter Agent Output (Detailed Evaluation)", expanded=False
                    ):
                        if agents.get("Recruiter_agent"):
                            for out in agents["Recruiter_agent"]:
                                st.write(out)
                        else:
                            st.write("No output captured from Recruiter_agent.")

                    st.markdown("---")

        # ---- WORKFLOW TAB ----
        with tab_workflow:
            st.markdown("### 📈 Multi-Agent Workflow")
            st.caption("Visual representation of how the agents interact.")
            try:
                st.image(
                    load_image("workflow.png"),
                    caption="Agent Workflow Graph",
                    use_column_width=True,
                )
            except Exception:
                st.warning("Workflow image not available.")


if __name__ == "__main__":
    main()
