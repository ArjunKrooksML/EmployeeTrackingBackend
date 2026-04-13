import resend
import config


def _send(to: str, subject: str, html: str):
    resend.api_key = config.RESEND_API_KEY
    resend.Emails.send({
        "from": config.FROM_EMAIL,
        "to": [to],
        "subject": subject,
        "html": html,
    })


def send_otp_email(to: str, otp: str):
    _send(
        to=to,
        subject="Your SVAAS Inframax OTP",
        html=f"""
            <p>Your OTP for password reset is:</p>
            <h2 style="letter-spacing:4px">{otp}</h2>
            <p>Valid for <strong>5 minutes</strong>. Do not share this with anyone.</p>
        """,
    )


def send_task_assigned_email(to: str, emp_name: str, task_name: str, description: str | None, deadline: str | None):
    deadline_line = f"<p><strong>Deadline:</strong> {deadline}</p>" if deadline else ""
    desc_line = f"<p>{description}</p>" if description else ""
    _send(
        to=to,
        subject=f"New Task Assigned: {task_name}",
        html=f"""
            <p>Hi {emp_name},</p>
            <p>A new task has been assigned to you:</p>
            <h3>{task_name}</h3>
            {desc_line}
            {deadline_line}
            <p>Log in to the portal to view full details.</p>
            <br/>
            <p style="color:#888;font-size:12px">SVAAS Inframax Solutions</p>
        """,
    )
