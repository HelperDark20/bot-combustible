# ==========================================
# IMPORTS
# ==========================================
import os

from openai import OpenAI

# ==========================================
# VARIABLES
# ==========================================
TOKEN = os.getenv("TOKEN")

OPENAI_API_KEY = os.getenv(
    "OPENAI_API_KEY"
)

CHAT_ID = os.getenv("CHAT_ID")

PORT = int(
    os.environ.get("PORT", 8080)
)

# ==========================================
# OPENAI CLIENT
# ==========================================
client = OpenAI(
    api_key=OPENAI_API_KEY
)

# ==========================================
# CONFIG COMBUSTIBLE DEFAULT
# ==========================================

DEFAULT_KM_L = 9.0

DEFAULT_VALOR_GALON = 15840

DEFAULT_TANQUE = 50000

# ==========================================
# VAPID KEYS
# ==========================================

VAPID_PRIVATE_KEY = os.getenv(
    "VAPID_PRIVATE_KEY"
)

VAPID_PUBLIC_KEY = os.getenv(
    "VAPID_PUBLIC_KEY"
)

VAPID_EMAIL = os.getenv(
    "VAPID_EMAIL",
    "mailto:admin@example.com"
)