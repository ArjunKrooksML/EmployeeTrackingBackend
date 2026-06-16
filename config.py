import os
from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{os.getenv('POSTGRES_USER', 'postgres')}:{os.getenv('POSTGRES_PASSWORD', 'root')}@"
    f"{os.getenv('POSTGRES_HOST', 'localhost')}:{os.getenv('POSTGRES_PORT', '5432')}/"
    f"{os.getenv('POSTGRES_DB', 'employee_mgmt')}"
)

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY is not set in environment")
JWT_ALGORITHM = "HS256"

# Token TTL (in seconds)
ACCESS_TOKEN_EXPIRE_SECONDS = int(os.getenv("ACCESS_TOKEN_EXPIRE_SECONDS", "900"))  
REFRESH_TOKEN_EXPIRE_SECONDS = int(os.getenv("REFRESH_TOKEN_EXPIRE_SECONDS", "604800")) 


ACCESS_TOKEN_EXPIRE_MINUTES = ACCESS_TOKEN_EXPIRE_SECONDS // 60
REFRESH_TOKEN_EXPIRE_DAYS = REFRESH_TOKEN_EXPIRE_SECONDS // 86400

# Email (Resend)
RESEND_API_KEY = os.getenv("RESEND_API", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "onboarding@resend.dev")
LOGO_URL = os.getenv("IMAGE", "")
PORTAL_URL = os.getenv("PORTAL_URL", "")

# Twilio WhatsApp
TWILIO_SID = os.getenv("TWILIO_SID", "")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN", "")
TWILIO_WA_FROM = os.getenv("TWILIO_WA_FROM", "")
TWILIO_WA_LEAVE_TEMPLATE = os.getenv("TWILIO_LEAVES", "")
TWILIO_WA_OTP_TEMPLATE = os.getenv("TWILIO_WA_OTP_TEMPLATE", "")
TWILIO_WA_TASK_TEMPLATE = os.getenv("TWILIO_WA_TASK_TEMPLATE", "")
TWILIO_WA_PAYSLIP_TEMPLATE = os.getenv("TWILIO_WA_PAYSLIP_TEMPLATE", "")


# Twilio SMS
TWILIO_SMS = os.getenv("TWILIO_SMS", "")

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# S3 / Supabase Storage
SUPABASE_S3_ENDPOINT = os.getenv("SUPABASE_S3_ENDPOINT", "")
SUPABASE_S3_REGION = os.getenv("SUPABASE_S3_REGION", "ap-south-1")
SUPABASE_S3_ACCESS_KEY = os.getenv("SUPABASE_S3_ACCESS_KEY", "")
SUPABASE_S3_SECRET_KEY = os.getenv("SUPABASE_S3_SECRET_KEY", "")
SUPABASE_S3_BUCKET = os.getenv("SUPABASE_S3_BUCKET", "")

