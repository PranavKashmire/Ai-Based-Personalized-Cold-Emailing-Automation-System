"""
csv_processor.py — Load, validate, and prepare leads CSV for processing.
"""

import re
import shutil
import logging
import pandas as pd
from datetime import datetime
from config import PROCESSED_CSV_PATH

logger = logging.getLogger(__name__)

# ── Regex patterns ───────────────────────────────────────────────────────────
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
URL_REGEX = re.compile(
    r"^(https?://)?"
    r"([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}"
    r"(/[^\s]*)?"
    r"$"
)

# ── Tracking columns added to CSV ────────────────────────────────────────────
TRACKING_COLUMNS = [
    "email_sent",
    "email_subject",
    "email_success",
    "sent_timestamp",
    "error_reason",
]


def normalize_url(url: str) -> str:
    """Ensure URL starts with https://"""
    url = url.strip()
    if not url.startswith("http"):
        url = "https://" + url
    return url


def validate_email(email: str) -> bool:
    return bool(EMAIL_REGEX.match(str(email).strip()))


def validate_url(url: str) -> bool:
    return bool(URL_REGEX.match(str(url).strip()))


def load_and_prepare_csv(input_csv_path: str) -> pd.DataFrame:
    """
    Load input CSV, add tracking columns, save as processed_leads.csv.
    Returns the DataFrame (includes ALL rows, invalid ones have error_reason set).
    """
    logger.info(f"Loading CSV: {input_csv_path}")
    df = pd.read_csv(input_csv_path, dtype=str).fillna("")

    # Ensure required columns exist
    if "store_url" not in df.columns or "email" not in df.columns:
        raise ValueError("CSV must contain 'store_url' and 'email' columns.")

    # Add optional columns if missing
    for col in ["store_name", "niche", "notes"]:
        if col not in df.columns:
            df[col] = ""

    # Add tracking columns
    for col in TRACKING_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    # Validate each row
    for idx, row in df.iterrows():
        errors = []
        url = str(row["store_url"]).strip()
        email = str(row["email"]).strip()

        if not url or not validate_url(url):
            errors.append("Invalid store_url")
        if not email or not validate_email(email):
            errors.append("Invalid email")

        if errors:
            df.at[idx, "email_success"] = "SKIP"
            df.at[idx, "error_reason"] = "; ".join(errors)
            logger.warning(f"Row {idx} skipped: {errors}")
        else:
            # Normalize URL
            df.at[idx, "store_url"] = normalize_url(url)
            # Derive store_name from URL if missing
            if not str(row.get("store_name", "")).strip():
                domain = url.replace("https://", "").replace("http://", "").split("/")[0]
                store_name = domain.replace("www.", "").split(".")[0].replace("-", " ").title()
                df.at[idx, "store_name"] = store_name

    # Save processed CSV
    df.to_csv(PROCESSED_CSV_PATH, index=False)
    logger.info(f"Processed CSV saved to: {PROCESSED_CSV_PATH}")

    total = len(df)
    valid = len(df[df["email_success"] != "SKIP"])
    logger.info(f"Total rows: {total} | Valid: {valid} | Skipped: {total - valid}")
    return df


def update_row(df: pd.DataFrame, idx: int, updates: dict) -> pd.DataFrame:
    """Update specific columns for a row and save CSV."""
    for col, val in updates.items():
        df.at[idx, col] = val
    df.to_csv(PROCESSED_CSV_PATH, index=False)
    return df


def get_valid_leads(df: pd.DataFrame) -> pd.DataFrame:
    """Return only rows that haven't been skipped or already sent."""
    return df[
        (df["email_success"] != "SKIP") &
        (df["email_success"] != "YES")
    ].copy()


if __name__ == "__main__":
    import sys
    import argparse

    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default="sample_leads.csv", help="Input CSV path")
    parser.add_argument("--test", action="store_true", help="Run with sample_leads.csv")
    args = parser.parse_args()

    csv_path = args.csv
    df = load_and_prepare_csv(csv_path)
    print(df[["store_url", "email", "store_name", "email_success", "error_reason"]].to_string())
    print(f"\nValid leads ready: {len(get_valid_leads(df))}")
