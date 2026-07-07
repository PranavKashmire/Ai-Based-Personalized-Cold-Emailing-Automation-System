"""
tracking.py — Update processed_leads.csv with email send results.
"""

import logging
from datetime import datetime, timezone
import pandas as pd
from config import PROCESSED_CSV_PATH

logger = logging.getLogger(__name__)


def get_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def record_send_result(
    df: pd.DataFrame,
    idx: int,
    email_body: str,
    subject: str,
    success: bool,
    error: str = "",
) -> pd.DataFrame:
    """
    Write email result data into the DataFrame row and save to CSV.
    """
    df.at[idx, "email_sent"] = email_body[:500] + "..." if len(email_body) > 500 else email_body
    df.at[idx, "email_subject"] = subject
    df.at[idx, "sent_timestamp"] = get_timestamp()
    df.at[idx, "email_success"] = "YES" if success else "NO"
    df.at[idx, "error_reason"] = error if not success else ""

    df.to_csv(PROCESSED_CSV_PATH, index=False)
    status = "✅ SUCCESS" if success else f"❌ FAILED: {error}"
    logger.info(f"Row {idx} tracked: {status}")
    return df


def get_success_count(df: pd.DataFrame) -> int:
    """Return number of successfully sent emails so far."""
    return int((df["email_success"] == "YES").sum())


def generate_summary_report(df: pd.DataFrame) -> str:
    total = len(df)
    sent = int((df["email_success"] == "YES").sum())
    failed = int((df["email_success"] == "NO").sum())
    skipped = int((df["email_success"] == "SKIP").sum())
    pending = total - sent - failed - skipped

    report = f"""
╔══════════════════════════════════════════════════════╗
║           SHOPIFY CRO OUTREACH — FINAL SUMMARY       ║
╠══════════════════════════════════════════════════════╣
║  Total Leads Processed : {total:<28}║
║  Emails Sent (Success) : {sent:<28}║
║  Emails Failed         : {failed:<28}║
║  Leads Skipped (Invalid): {skipped:<27}║
║  Remaining (Not Sent)  : {pending:<28}║
╠══════════════════════════════════════════════════════╣
║  Processed CSV         : output/processed_leads.csv  ║
╚══════════════════════════════════════════════════════╝
""".strip()

    # Top errors
    if failed > 0:
        error_df = df[df["email_success"] == "NO"][["email", "error_reason"]]
        report += "\n\n📋 FAILED SENDS:\n"
        for _, row in error_df.iterrows():
            report += f"  • {row['email']}: {row['error_reason']}\n"

    return report
