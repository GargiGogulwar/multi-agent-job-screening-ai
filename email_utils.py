import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_interview_email(
    from_email: str,
    from_password: str,
    to_email: str,
    candidate_name: str,
    score: int,
):
    """
    Send a simple interview invitation email.

    - from_email: company / HR email address (Gmail recommended)
    - from_password: app-specific password (NOT the normal Gmail password)
    - to_email: candidate email address
    - candidate_name: name to use in the email greeting
    - score: candidate's match score (for context in email body)

    Returns:
        True if email sent successfully,
        or an error message string if something goes wrong.
    """
    if not from_email or not from_password:
        return "Sender email or app password is missing."

    if not to_email:
        return "Candidate email is missing."

    subject = "Interview Invitation - Shortlisted for the Role"

    body = f"""
Hi {candidate_name},

Congratulations! Based on our evaluation of your profile, you have been shortlisted
with a match score of {score}/100.

We would like to invite you for the next round of the interview process.

Please reply to this email with your availability for the next 3–5 working days.

Best regards,
AI Recruitment Assistant
(on behalf of the Hiring Team)
"""

    # Compose the email
    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        # Use Gmail's SMTP server (works for most Gmail / Google Workspace accounts)
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(from_email, from_password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        return f"Error sending email: {e}"
