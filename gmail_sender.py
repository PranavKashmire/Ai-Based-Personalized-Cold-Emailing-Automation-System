"""
gmail_sender.py — Send emails via Gmail API OAuth2 with PDF attachment.
"""

import os
import base64
import time
import logging
import mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import CLIENT_SECRET_PATH, TOKEN_PATH, GMAIL_SCOPES, SENDER_EMAIL, RETRY_LIMIT

logger = logging.getLogger(__name__)


def get_gmail_service():
    """Authenticate and return Gmail API service. Caches token.json after first auth."""
    creds = None

    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, GMAIL_SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRET_PATH):
                raise FileNotFoundError(
                    f"Gmail OAuth credentials not found at: {CLIENT_SECRET_PATH}\n"
                    "Please download client_secret.json from Google Cloud Console "
                    "and place it in the 'credentials/' folder."
                )
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_PATH, GMAIL_SCOPES)
            creds = flow.run_local_server(port=0)

        # Save token for next run
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())
        logger.info("Gmail OAuth token saved to token.json")

    return build("gmail", "v1", credentials=creds)


def build_message(to: str, subject: str, body: str, pdf_path: str | None = None) -> dict:
    """Build MIME email with optional PDF attachment."""
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = to
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain", "utf-8"))

    # Attach PDF
    if pdf_path and os.path.exists(pdf_path):
        mime_type, _ = mimetypes.guess_type(pdf_path)
        if mime_type is None:
            mime_type = "application/octet-stream"
        main_type, sub_type = mime_type.split("/", 1)

        with open(pdf_path, "rb") as f:
            attachment = MIMEBase(main_type, sub_type)
            attachment.set_payload(f.read())
            encoders.encode_base64(attachment)
            attachment.add_header(
                "Content-Disposition",
                "attachment",
                filename=os.path.basename(pdf_path)
            )
            msg.attach(attachment)
        logger.debug(f"Attached PDF: {pdf_path}")
    elif pdf_path:
        logger.warning(f"PDF not found for attachment: {pdf_path}")

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return {"raw": raw}


def send_email(
    to: str,
    subject: str,
    body: str,
    pdf_path: str | None = None,
    service=None
) -> tuple[bool, str]:
    """
    Send an email via Gmail API.
    Returns (success: bool, error_message: str)
    """
    if service is None:
        try:
            service = get_gmail_service()
        except Exception as e:
            return False, f"Gmail auth failed: {e}"

    message = build_message(to, subject, body, pdf_path)

    for attempt in range(1, RETRY_LIMIT + 2):  # 1 initial + RETRY_LIMIT retries
        try:
            sent = service.users().messages().send(userId="me", body=message).execute()
            logger.info(f"Email sent to {to} | Message ID: {sent.get('id')} | Attempt: {attempt}")
            return True, ""
        except HttpError as e:
            error_str = str(e)
            logger.warning(f"Send attempt {attempt} failed for {to}: {error_str}")
            if attempt <= RETRY_LIMIT:
                logger.info(f"Retrying in 5 seconds...")
                time.sleep(5)
            else:
                return False, error_str
        except Exception as e:
            error_str = str(e)
            logger.error(f"Unexpected error sending to {to}: {error_str}")
            if attempt <= RETRY_LIMIT:
                time.sleep(5)
            else:
                return False, error_str

    return False, "Max retries exceeded"


if __name__ == "__main__":
    import argparse
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("--to", required=True, help="Recipient email address")
    parser.add_argument("--subject", default="Test Email from CRO Agent")
    parser.add_argument("--body", default="This is a test email from the Shopify CRO Outreach Agent.")
    parser.add_argument("--pdf", default=None, help="Path to PDF to attach")
    args = parser.parse_args()

    success, error = send_email(args.to, args.subject, args.body, args.pdf)
    if success:
        print(f"✅ Email sent successfully to {args.to}")
    else:
        print(f"❌ Failed: {error}")
