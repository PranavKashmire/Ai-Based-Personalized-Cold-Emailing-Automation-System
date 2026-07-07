"""
bulk_sender.py — Send cold emails to recruitment agencies from CSV.
Sends one-by-one, updates status in CSV, stores thread IDs for follow-up.
"""
import os
import sys
import csv
import time
import base64
import logging
import random
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gmail_sender import get_gmail_service
from config import SENDER_EMAIL

# ── Configuration ────────────────────────────────────────────────────────────
CSV_PATH = os.path.join(os.path.dirname(__file__), "pune_recruitment_leads.csv")
# Delay configurations for natural randomization
DELAY_MIN = 5     # min delay in seconds
DELAY_MAX = 35    # max delay in seconds
SUBJECT = "AI Resume Screening Agent for Recruitment Agencies"

EMAIL_TEMPLATE = """Hi {agency_name},

My name is Pranav Kashmire, and I build AI automation solutions for recruitment agencies.

I noticed that recruiters often spend hours manually reviewing resumes before identifying the most suitable candidates. For agencies handling multiple openings, this can consume a significant amount of time every week.

To solve this, I have built an AI Resume Screening Agent that can analyze hundreds of resumes in bulk, compare them against a job description, and automatically rank the best candidates based on skills, experience, and relevance.

Benefits:

✓ Screen hundreds of resumes within minutes
✓ Automatically rank candidates against the JD
✓ Reduce manual screening effort by up to 4 minutes per resume
✓ Save 20–30+ recruiter hours on high-volume hiring roles
✓ Deliver consistent candidate evaluation

The goal is not to replace recruiters but to help them focus on interviews, client communication, and placements instead of repetitive screening work.

I'd be happy to run a free sample screening using one of your current job openings so you can see the results yourself.

If interested, simply reply to this email with "Interested" and I'll share a quick demo.

Best regards,

Pranav Kashmire
AI Engineer & AI Automation Consultant
My LinkedIn: http://www.linkedin.com/in/pranav-kashmire-a1595621b
📞 Phone / WhatsApp: +91 8329750737
"""

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            os.path.join(os.path.dirname(__file__), "logs",
                         f"bulk_send_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
            encoding="utf-8"
        ),
    ]
)
logger = logging.getLogger("bulk_sender")


def send_single_email(service, to_email, agency_name):
    """Send one email and return (success, message_id, thread_id, error)."""
    body = EMAIL_TEMPLATE.format(agency_name=agency_name)

    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email
    msg["Subject"] = SUBJECT
    msg.attach(MIMEText(body, "plain", "utf-8"))

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    message = {"raw": raw}

    try:
        sent = service.users().messages().send(userId="me", body=message).execute()
        msg_id = sent.get("id", "")
        thread_id = sent.get("threadId", "")
        logger.info(f"  SENT to {to_email} | msgId={msg_id} | threadId={thread_id}")
        return True, msg_id, thread_id, ""
    except Exception as e:
        error = str(e)
        logger.error(f"  FAILED for {to_email}: {error}")
        return False, "", "", error


def load_csv(path):
    """Load CSV as list of dicts."""
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return rows


def save_csv(path, rows, fieldnames):
    """Save list of dicts back to CSV."""
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run():
    logger.info("=" * 60)
    logger.info("  BULK EMAIL SENDER — Recruitment Agency Outreach")
    logger.info("=" * 60)

    # Load leads
    rows = load_csv(CSV_PATH)
    logger.info(f"Loaded {len(rows)} leads from CSV")

    # Ensure tracking columns exist
    fieldnames = list(rows[0].keys()) if rows else []
    for col in ["status", "message_id", "thread_id", "sent_at", "error"]:
        if col not in fieldnames:
            fieldnames.append(col)
            for row in rows:
                row[col] = ""

    # Count pending
    pending = [r for r in rows if r.get("status", "pending") == "pending"]
    logger.info(f"Pending to send: {len(pending)}")

    if not pending:
        logger.info("No pending emails. All done!")
        return

    # Authenticate Gmail
    logger.info("Authenticating Gmail API...")
    try:
        service = get_gmail_service()
        logger.info("Gmail authenticated OK")
    except Exception as e:
        logger.critical(f"Gmail auth failed: {e}")
        sys.exit(1)

    # Send loop
    sent_count = 0
    fail_count = 0

    for i, row in enumerate(rows):
        if row.get("status") != "pending":
            continue

        agency_name = row.get("agency_name", "Team")
        # Decide which email to use: prefer founder_email, fallback to agency_email
        to_email = row.get("founder_email", "").strip() or row.get("agency_email", "").strip()

        if not to_email:
            logger.warning(f"  SKIP {agency_name}: no email address")
            row["status"] = "skipped"
            row["error"] = "no email"
            continue

        logger.info(f"[{sent_count + fail_count + 1}/{len(pending)}] Sending to {agency_name} <{to_email}>...")

        success, msg_id, thread_id, error = send_single_email(service, to_email, agency_name)

        row["status"] = "sent" if success else "failed"
        row["message_id"] = msg_id
        row["thread_id"] = thread_id
        row["sent_at"] = datetime.now().isoformat() if success else ""
        row["error"] = error

        if success:
            sent_count += 1
        else:
            fail_count += 1

        # Save CSV after every email (crash-safe)
        save_csv(CSV_PATH, rows, fieldnames)

        # Delay before next send
        remaining = len(pending) - (sent_count + fail_count)
        if remaining > 0:
            current_delay = random.choice([5, 10, 15, 20, 25, 30, 35])
            logger.info(f"  Waiting {current_delay}s before next send... ({remaining} remaining)")
            time.sleep(current_delay)

    # Final summary
    logger.info("=" * 60)
    logger.info("  CAMPAIGN COMPLETE")
    logger.info(f"  Sent: {sent_count}")
    logger.info(f"  Failed: {fail_count}")
    logger.info(f"  Skipped: {len([r for r in rows if r.get('status') == 'skipped'])}")
    logger.info(f"  CSV updated: {CSV_PATH}")
    logger.info("=" * 60)


if __name__ == "__main__":
    run()
