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
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"

# Token TTL (in seconds)
ACCESS_TOKEN_EXPIRE_SECONDS = int(os.getenv("ACCESS_TOKEN_EXPIRE_SECONDS", "900"))  
REFRESH_TOKEN_EXPIRE_SECONDS = int(os.getenv("REFRESH_TOKEN_EXPIRE_SECONDS", "604800")) 


ACCESS_TOKEN_EXPIRE_MINUTES = ACCESS_TOKEN_EXPIRE_SECONDS // 60
REFRESH_TOKEN_EXPIRE_DAYS = REFRESH_TOKEN_EXPIRE_SECONDS // 86400

# Email (Resend)
RESEND_API_KEY = os.getenv("RESEND_API", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "onboarding@resend.dev")

