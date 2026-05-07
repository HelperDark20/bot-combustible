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