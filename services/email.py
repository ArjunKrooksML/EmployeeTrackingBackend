import resend
import config

_LOGO_SRC = config.LOGO_URL


def _footer() -> str:
    logo_html = (
        f'<img src="{_LOGO_SRC}" alt="SVAAS" width="36" height="36" '
        'style="border-radius:8px;vertical-align:middle;margin-right:10px;" />'
        if _LOGO_SRC else ""
    )
    return f"""
    <div style="margin-top:40px;padding-top:20px;border-top:1px solid #e5e7eb;
                text-align:center;color:#6b7280;font-size:12px;">
        <div style="display:inline-flex;align-items:center;justify-content:center;">
            {logo_html}
            <span style="font-weight:600;font-size:13px;color:#374151;
                         vertical-align:middle;">SVAAS Inframax Solutions</span>
        </div>
        <p style="margin:6px 0 0;font-size:11px;color:#9ca3af;">
            This is an automated message. Please do not reply.
        </p>
    </div>
    """


def _wrap(body: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8" /></head>
    <body style="margin:0;padding:0;background:#f3f4f6;font-family:'Segoe UI',Arial,sans-serif;">
        <div style="max-width:560px;margin:32px auto;background:#ffffff;
                    border-radius:12px;box-shadow:0 1px 4px rgba(0,0,0,.08);
                    overflow:hidden;">
            <!-- Header bar -->
            <div style="background:#130c24;padding:20px 32px;display:flex;align-items:center;gap:12px;">
                {'<img src="' + _LOGO_SRC + '" alt="SVAAS" width="36" height="36" style="border-radius:8px;" />' if _LOGO_SRC else ""}
                <span style="color:#ffffff;font-size:15px;font-weight:600;letter-spacing:.3px;">
                    SVAAS Inframax Solutions
                </span>
            </div>
            <!-- Body -->
            <div style="padding:32px;">
                {body}
                {_footer()}
            </div>
        </div>
    </body>
    </html>
    """


def _send(to: str, subject: str, html: str):
    resend.api_key = config.RESEND_API_KEY
    resend.Emails.send({
        "from": config.FROM_EMAIL,
        "to": [to],
        "subject": subject,
        "html": html,
    })


def send_otp_email(to: str, otp: str):
    body = f"""
        <h2 style="margin:0 0 8px;font-size:20px;color:#111827;">Password Reset OTP</h2>
        <p style="margin:0 0 24px;color:#6b7280;font-size:14px;line-height:1.6;">
            Use the code below to reset your password. It expires in <strong>5 minutes</strong>.
        </p>
        <div style="background:#f5f3ff;border:1px solid #ddd6fe;border-radius:10px;
                    padding:20px;text-align:center;margin-bottom:20px;">
            <span style="font-size:36px;font-weight:700;letter-spacing:10px;
                         color:#4f46e5;font-family:monospace;">{otp}</span>
        </div>
        <p style="margin:0;color:#9ca3af;font-size:12px;">
            Do not share this code with anyone. If you did not request a password reset,
            you can safely ignore this email.
        </p>
    """
    _send(to=to, subject="Your SVAAS Inframax OTP", html=_wrap(body))


def send_task_assigned_email(
    to: str, emp_name: str, task_name: str,
    description: str | None, deadline: str | None
):
    deadline_row = (
        f"""
        <tr>
            <td style="padding:10px 14px;color:#6b7280;font-size:13px;
                       white-space:nowrap;font-weight:500;">Deadline</td>
            <td style="padding:10px 14px;color:#111827;font-size:13px;">{deadline}</td>
        </tr>
        """
        if deadline else ""
    )
    desc_block = (
        f"""
        <div style="margin:16px 0;padding:14px;background:#f8fafc;border-radius:8px;
                    border-left:3px solid #6366f1;">
            <p style="margin:0;color:#374151;font-size:13px;line-height:1.6;">{description}</p>
        </div>
        """
        if description else ""
    )
    body = f"""
        <p style="margin:0 0 20px;color:#374151;font-size:14px;">
            Hi <strong>{emp_name}</strong>,
        </p>
        <p style="margin:0 0 20px;color:#374151;font-size:14px;line-height:1.6;">
            A new task has been assigned to you on the SVAAS employee portal.
        </p>

        <!-- Task card -->
        <div style="border:1px solid #e5e7eb;border-radius:10px;overflow:hidden;margin-bottom:20px;">
            <!-- Task name header -->
            <div style="background:#4f46e5;padding:14px 18px;">
                <span style="color:#ffffff;font-size:15px;font-weight:600;">{task_name}</span>
            </div>
            <!-- Task details table -->
            <table style="width:100%;border-collapse:collapse;">
                <tbody>
                    {deadline_row}
                </tbody>
            </table>
            {desc_block}
        </div>

        <a href="{config.PORTAL_URL}" style="display:inline-block;background:#4f46e5;color:#ffffff;
                           font-size:13px;font-weight:600;padding:10px 22px;
                           border-radius:8px;text-decoration:none;">
            View in Portal
        </a>
    """
    _send(
        to=to,
        subject=f"New Task Assigned: {task_name}",
        html=_wrap(body),
    )
