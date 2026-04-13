import random
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from database.models import OtpToken


def gen_otp(email: str, db: Session) -> str:
    otp = str(random.randint(100000, 999999))
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
    # upsert — replace any existing OTP for this email
    record = db.query(OtpToken).filter(OtpToken.email == email).first()
    if record:
        record.otp = otp
        record.expires_at = expires_at
    else:
        db.add(OtpToken(email=email, otp=otp, expires_at=expires_at))
    db.commit()
    return otp


def verify_otp(email: str, otp: str, db: Session) -> bool:
    record = db.query(OtpToken).filter(OtpToken.email == email).first()
    if not record:
        return False
    expires = record.expires_at.replace(tzinfo=timezone.utc) if record.expires_at.tzinfo is None else record.expires_at
    if datetime.now(timezone.utc) > expires:
        db.delete(record)
        db.commit()
        return False
    if record.otp != otp:
        return False
    db.delete(record)  # single use
    db.commit()
    return True
