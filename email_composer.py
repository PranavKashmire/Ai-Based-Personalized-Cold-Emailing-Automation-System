"""
email_composer.py — Personalize outreach email with audit-specific insights.
"""

import re
import logging
from config import EMAIL_TEMPLATE_PATH, SIGNATURE

logger = logging.getLogger(__name__)

# ── Spam trigger words to avoid ──────────────────────────────────────────────
SPAM_WORDS = re.compile(
    r"\b(free money|guaranteed|act now|limited time offer|click here|winner|"
    r"risk free|earn \$|100% free|no cost|exclusive deal|urgent|you've been selected)\b",
    re.IGNORECASE
)


def load_template() -> str:
    try:
        with open(EMAIL_TEMPLATE_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"Email template not found at {EMAIL_TEMPLATE_PATH}")
        return ""


def pick_top_insights(audit: dict, n: int = 2) -> list[str]:
    """Extract top N most impactful audit findings as plain-language sentences."""
    insights = []
    
    # Iterate through all issues, preferring "High" impact
    for issue in audit.get("all_issues", []):
        if issue.get("impact_level") == "High":
            problem = issue.get("problem", "")
            if problem and problem not in insights:
                insights.append(problem)
        if len(insights) >= n:
            break

    # Final fallback
    while len(insights) < n:
        insights.append("a key conversion bottleneck that's reducing your sales potential")

    return insights[:n]


def generate_subject(store_name: str, audit: dict) -> str:
    """
    Generate a unique, personalized subject line under 60 characters.
    Picks a variation based on the top audit finding.
    """
    score = audit.get("overall_score", 0)
    top_issues = [i for i in audit.get("all_issues", []) if i.get("impact_level") == "High"]

    niche = audit.get("niche", "").strip()

    # Build subject options based on audit data
    candidates = [
        f"Your {store_name} store is leaving revenue on table",
        f"Quick CRO audit for {store_name} — 3 things I spotted",
        f"I audited {store_name} and found {len(top_issues)} gaps",
        f"{store_name}: free CRO audit inside",
        f"Spotted a CRO issue on {store_name} (audit attached)",
        f"Your {store_name} store could convert 20% better",
    ]

    if niche:
        candidates.insert(0, f"CRO audit for your {niche} store — {store_name}")

    # Pick subject under 60 chars, no spam triggers
    for subject in candidates:
        if len(subject) <= 60 and not SPAM_WORDS.search(subject):
            return subject

    # Fallback: trim longest
    fallback = f"CRO audit for {store_name}"
    return fallback[:60]


def personalize_email(store_name: str, audit: dict) -> tuple[str, str]:
    """
    Returns (subject, body) for the personalized outreach email.
    """
    template = load_template()
    if not template:
        logger.error("Empty template — cannot compose email")
        return "", ""

    insights = pick_top_insights(audit, n=2)
    insight_1 = insights[0]
    insight_2 = insights[1]

    subject = generate_subject(store_name, audit)

    # Format insights conversationally
    body = template.replace("{{store_name}}", store_name)
    body = body.replace("{{subject}}", subject)
    body = body.replace("{{audit_insight_1}}", insight_1.lower().rstrip("."))
    body = body.replace("{{audit_insight_2}}", insight_2.lower().rstrip("."))
    body = body.replace("{{signature}}", SIGNATURE)

    # Remove subject line from body (it's in the header)
    body = "\n".join(
        line for line in body.splitlines()
        if not line.strip().lower().startswith("subject:")
    ).strip()

    # Sanity check — remove spam words (defensive)
    if SPAM_WORDS.search(body):
        logger.warning(f"Potential spam words detected in email body for {store_name}")

    logger.info(f"Email composed for {store_name} | Subject: {subject}")
    return subject, body


if __name__ == "__main__":
    import argparse, json
    logging.basicConfig(level=logging.INFO)

    dummy_audit = {
        "store_name": "Test Store",
        "overall_score": 55,
        "niche": "skincare",
        "top_10_improvements": [
            {"problem": "No email capture popup found on homepage", "impact": "High"},
            {"problem": "Missing urgency signals on product pages", "impact": "High"},
        ],
        "categories": [],
        "hidden_opportunities": [],
    }

    subject, body = personalize_email("Test Store", dummy_audit)
    print(f"Subject: {subject}\n")
    print("Body:")
    print(body)
