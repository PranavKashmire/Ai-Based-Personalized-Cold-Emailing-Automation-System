"""
main.py — Orchestrator for the Shopify CRO Cold Outreach Agent.

Usage:
    python main.py --csv leads.csv
    python main.py --csv leads.csv --dry-run   # Process without sending emails
"""

import os
import sys
import time
import logging
import argparse
from datetime import datetime

from config import MAX_EMAILS, SEND_DELAY, LOGS_DIR
from csv_processor import load_and_prepare_csv, get_valid_leads, update_row
from store_auditor import audit_store
from screenshot_capture import capture_screenshots
from pdf_generator import generate_pdf
from email_composer import personalize_email
from gmail_sender import get_gmail_service, send_email
from tracking import record_send_result, get_success_count, generate_summary_report

# ── Logging Setup ────────────────────────────────────────────────────────────
log_filename = os.path.join(LOGS_DIR, f"agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(log_filename, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger("main")


def print_banner():
    banner = """
╔══════════════════════════════════════════════════════════════╗
║         SHOPIFY CRO OUTREACH AGENT  —  v1.0                 ║
║         Automated Audit + Personalized Cold Email            ║
╚══════════════════════════════════════════════════════════════╝
    """.strip()
    print(banner)


def run_pipeline(csv_path: str, dry_run: bool = False):
    print_banner()
    logger.info(f"Pipeline started | CSV: {csv_path} | Dry run: {dry_run}")

    # ── Step 1 & 2: Load and validate CSV ────────────────────────────────────
    logger.info("=" * 60)
    logger.info("STEP 1-2: Loading and validating CSV...")
    try:
        df = load_and_prepare_csv(csv_path)
    except Exception as e:
        logger.critical(f"Failed to load CSV: {e}")
        sys.exit(1)

    valid_leads = get_valid_leads(df)
    logger.info(f"Valid leads ready for processing: {len(valid_leads)}")

    if len(valid_leads) == 0:
        logger.warning("No valid leads found. Exiting.")
        return

    # ── Gmail Service ─────────────────────────────────────────────────────────
    gmail_service = None
    if not dry_run:
        logger.info("Authenticating with Gmail API...")
        try:
            gmail_service = get_gmail_service()
            logger.info("Gmail API authenticated successfully ✅")
        except FileNotFoundError as e:
            logger.critical(str(e))
            sys.exit(1)
        except Exception as e:
            logger.critical(f"Gmail authentication failed: {e}")
            sys.exit(1)

    # ── Main Pipeline Loop ────────────────────────────────────────────────────
    success_count = get_success_count(df)
    logger.info(f"Previously sent: {success_count} | Limit: {MAX_EMAILS}")

    for idx, row in valid_leads.iterrows():
        # ── Outreach limit check ─────────────────────────────────────────────
        if success_count >= MAX_EMAILS:
            logger.info(f"🛑 Reached {MAX_EMAILS} successful emails. Stopping outreach.")
            break

        store_url = row["store_url"]
        email = row["email"]
        store_name = row["store_name"] or "Your Store"
        niche = row.get("niche", "")

        logger.info("=" * 60)
        logger.info(f"Processing: {store_name} | {store_url} | {email}")

        # ── Step 3: Audit ────────────────────────────────────────────────────
        logger.info("STEP 3: Running store audit...")
        try:
            audit = audit_store(store_url, store_name=store_name, niche=niche)
        except Exception as e:
            logger.error(f"Audit failed for {store_url}: {e}")
            df = update_row(df, idx, {"email_success": "NO", "error_reason": f"Audit error: {e}"})
            continue

        if audit.get("error"):
            logger.warning(f"Audit returned error for {store_url}: {audit['error']}")
            # Continue anyway — we'll use partial data

        # ── Step 4: Screenshots ──────────────────────────────────────────────
        logger.info("STEP 4: Capturing screenshots...")
        try:
            screenshots = capture_screenshots(
                store_url,
                store_name,
                product_url=audit.get("product_page_url")
            )
            logger.info(f"Captured {len(screenshots)} screenshots")
        except Exception as e:
            logger.warning(f"Screenshot step failed (continuing): {e}")
            screenshots = []

        # ── Step 5: Generate PDF ─────────────────────────────────────────────
        logger.info("STEP 5: Generating audit PDF...")
        pdf_path = None
        try:
            pdf_path = generate_pdf(audit, screenshot_paths=screenshots)
            if pdf_path:
                logger.info(f"PDF saved: {pdf_path}")
            else:
                logger.warning("PDF generation returned None — continuing without attachment")
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")

        # ── Step 6: Personalize Email ────────────────────────────────────────
        logger.info("STEP 6: Composing personalized email...")
        try:
            subject, body = personalize_email(store_name, audit)
            if not subject or not body:
                raise ValueError("Empty subject or body")
        except Exception as e:
            logger.error(f"Email composition failed: {e}")
            df = update_row(df, idx, {"email_success": "NO", "error_reason": f"Compose error: {e}"})
            continue

        # ── Step 7: Send Email ───────────────────────────────────────────────
        logger.info(f"STEP 7: Sending email to {email}...")

        if dry_run:
            logger.info(f"[DRY RUN] Would send to: {email}")
            logger.info(f"[DRY RUN] Subject: {subject}")
            logger.info(f"[DRY RUN] PDF: {pdf_path}")
            success, error = True, ""
        else:
            success, error = send_email(
                to=email,
                subject=subject,
                body=body,
                pdf_path=pdf_path,
                service=gmail_service
            )

        # ── Step 8: Track result ─────────────────────────────────────────────
        df = record_send_result(df, idx, body, subject, success, error)

        if success:
            success_count += 1
            logger.info(f"✅ [{success_count}/{MAX_EMAILS}] Email sent: {email}")
        else:
            logger.warning(f"❌ Email failed for {email}: {error}")

        # Delay between sends
        if not dry_run and success_count < MAX_EMAILS:
            logger.info(f"Waiting {SEND_DELAY}s before next send...")
            time.sleep(SEND_DELAY)

    # ── Step 10: Final Summary ────────────────────────────────────────────────
    logger.info("=" * 60)
    logger.info("GENERATING FINAL SUMMARY REPORT...")
    summary = generate_summary_report(df)
    print("\n" + summary)

    # Save summary to file
    summary_path = os.path.join("output", "summary_report.txt")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(summary)
    logger.info(f"Summary report saved: {summary_path}")
    logger.info("Pipeline complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Shopify CRO Outreach Agent — Audit stores and send personalized emails"
    )
    parser.add_argument(
        "--csv",
        required=True,
        help="Path to input CSV file with leads (must have store_url and email columns)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Process leads and generate PDFs without actually sending emails"
    )
    args = parser.parse_args()

    if not os.path.exists(args.csv):
        print(f"❌ CSV file not found: {args.csv}")
        sys.exit(1)

    run_pipeline(csv_path=args.csv, dry_run=args.dry_run)
