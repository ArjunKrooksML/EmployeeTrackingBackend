import re
from twilio.rest import Client
import config


def _client() -> Client:
    return Client(config.TWILIO_SID, config.TWILIO_TOKEN)


def _fmt_phone(phone: str) -> str:
    digits = re.sub(r"\D", "", phone)
    # Always treat as Indian number — use last 10 digits
    return f"whatsapp:+91{digits[-10:]}"


def _send(to_phone: str, body: str, template_sid: str = ""):
    print(f"[whatsapp] TWILIO_SID set: {bool(config.TWILIO_SID)}")
    print(f"[whatsapp] TWILIO_WA_FROM: {config.TWILIO_WA_FROM!r}")
    if not config.TWILIO_SID or not config.TWILIO_WA_FROM:
        print("[whatsapp] Aborting — TWILIO_SID or TWILIO_WA_FROM not set in env")
        return
    wa_to = _fmt_phone(to_phone)
    print(f"[whatsapp] Sending to {wa_to} | template_sid: {template_sid!r}")
    client = _client()
    try:
        if template_sid:
            msg = client.messages.create(
                from_=config.TWILIO_WA_FROM,
                to=wa_to,
                content_sid=template_sid,
            )
        else:
            msg = client.messages.create(
                from_=config.TWILIO_WA_FROM,
                to=wa_to,
                body=body,
            )
        print(f"[whatsapp] Sent OK — SID: {msg.sid} | status: {msg.status}")
    except Exception as e:
        print(f"[whatsapp] ERROR sending to {wa_to}: {type(e).__name__}: {e}")


def send_otp_whatsapp(phone: str, otp: str):
    print(f"[whatsapp] send_otp_whatsapp called — phone: {phone!r}")
    body = (
        f"Your SVAAS Inframax OTP is: *{otp}*\n"
        f"Valid for 5 minutes. Do not share this with anyone."
    )
    _send(phone, body, config.TWILIO_WA_OTP_TEMPLATE)


def send_task_whatsapp(phone: str, emp_name: str, task_name: str, deadline: str | None):
    print(f"[whatsapp] send_task_whatsapp called — phone: {phone!r}, task: {task_name!r}")
    deadline_line = f"\n📅 Deadline: {deadline}" if deadline else ""
    body = (
        f"Hi {emp_name}, a new task has been assigned to you on the SVAAS portal.\n\n"
        f"📋 *{task_name}*{deadline_line}\n\n"
        f"Log in to view full details: {config.PORTAL_URL}"
    )
    _send(phone, body, config.TWILIO_WA_TASK_TEMPLATE)


def send_otp_sms(phone: str, otp: str):
    print(f"[sms] send_otp_sms called — phone: {phone!r}")
    if not config.TWILIO_SID or not config.TWILIO_SMS:
        print("[sms] Aborting — TWILIO_SID or TWILIO_SMS not set in env")
        return
    digits = re.sub(r"\D", "", phone)
    sms_to = f"+91{digits[-10:]}"
    body = f"Your SVAAS Inframax OTP is: {otp}\nValid for 5 minutes. Do not share this with anyone."
    try:
        client = _client()
        msg = client.messages.create(from_=config.TWILIO_SMS, to=sms_to, body=body)
        print(f"[sms] OTP sent OK — SID: {msg.sid} | status: {msg.status}")
    except Exception as e:
        print(f"[sms] ERROR sending OTP to {sms_to}: {type(e).__name__}: {e}")


def send_task_sms(phone: str, emp_name: str, task_name: str, deadline: str | None):
    print(f"[sms] send_task_sms called — phone: {phone!r}, task: {task_name!r}")
    if not config.TWILIO_SID or not config.TWILIO_SMS:
        print("[sms] Aborting — TWILIO_SID or TWILIO_SMS not set in env")
        return
    digits = re.sub(r"\D", "", phone)
    sms_to = f"+91{digits[-10:]}"
    deadline_line = f"\nDeadline: {deadline}" if deadline else ""
    body = (
        f"Hi {emp_name}, a new task has been assigned to you on the SVAAS portal.\n"
        f"Task: {task_name}{deadline_line}\n"
        f"Login: {config.PORTAL_URL}"
    )
    try:
        client = _client()
        msg = client.messages.create(from_=config.TWILIO_SMS, to=sms_to, body=body)
        print(f"[sms] Sent OK — SID: {msg.sid} | status: {msg.status}")
    except Exception as e:
        print(f"[sms] ERROR sending to {sms_to}: {type(e).__name__}: {e}")
