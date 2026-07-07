"""
config.py — Centralized configuration for the Shopify CRO Outreach Agent
"""

import os

# ── Base Paths ──────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
PDF_DIR = os.path.join(OUTPUT_DIR, "pdfs")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
CREDENTIALS_DIR = os.path.join(BASE_DIR, "credentials")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

PROCESSED_CSV_PATH = os.path.join(OUTPUT_DIR, "processed_leads.csv")
LOG_FILE_PATH = os.path.join(LOGS_DIR, "agent.log")
CLIENT_SECRET_PATH = os.path.join(CREDENTIALS_DIR, "client_secret.json")
TOKEN_PATH = os.path.join(CREDENTIALS_DIR, "token.json")
EMAIL_TEMPLATE_PATH = os.path.join(TEMPLATES_DIR, "email_template.txt")

# ── Outreach Limits ─────────────────────────────────────────────────────────
MAX_EMAILS = 100          # Stop outreach after this many successful sends
RETRY_LIMIT = 2           # Number of send retries on failure
SEND_DELAY = 10           # Seconds to wait between sends

# ── Sender Information ──────────────────────────────────────────────────────
SENDER_NAME = "Pranav Kashmire"
SENDER_EMAIL = "pranav.kashmire09@gmail.com"
SENDER_TITLE = "Shopify Developer"

SIGNATURE = f"""
Regards,
{SENDER_NAME}
{SENDER_TITLE}
Email : {SENDER_EMAIL}
""".strip()

# ── Gmail API Scopes ────────────────────────────────────────────────────────
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

# ── Audit Settings ──────────────────────────────────────────────────────────
REQUEST_TIMEOUT = 15      # Seconds for HTTP requests to store
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

# ── Ensure directories exist ────────────────────────────────────────────────
for _dir in [OUTPUT_DIR, PDF_DIR, LOGS_DIR, CREDENTIALS_DIR, TEMPLATES_DIR]:
    os.makedirs(_dir, exist_ok=True)
