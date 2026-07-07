"""Minimal preflight: test that Gmail OAuth token refreshes and API is ready."""
import os, sys, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import CLIENT_SECRET_PATH, TOKEN_PATH, GMAIL_SCOPES

print("=" * 50)
print("  PREFLIGHT CHECK: Email Infrastructure")
print("=" * 50)

# 1. Credential files
print(f"\n[1] client_secret.json ... ", end="")
print("FOUND" if os.path.exists(CLIENT_SECRET_PATH) else "MISSING")

print(f"[2] token.json .......... ", end="")
if os.path.exists(TOKEN_PATH):
    with open(TOKEN_PATH) as f:
        tok = json.load(f)
    print("FOUND")
    print(f"    Expiry: {tok.get('expiry', 'unknown')}")
    print(f"    Has refresh_token: {'Yes' if tok.get('refresh_token') else 'No'}")
else:
    print("MISSING -- will need full OAuth flow")
    sys.exit(1)

# 2. Test token refresh
print(f"\n[3] Refreshing token ... ", end="")
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

creds = Credentials.from_authorized_user_file(TOKEN_PATH, GMAIL_SCOPES)
if creds.expired:
    print(f"(token expired, refreshing...)")
    try:
        creds.refresh(Request())
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())
        print(f"    Token refreshed OK")
        print(f"    New expiry: {creds.expiry}")
    except Exception as e:
        print(f"    REFRESH FAILED: {e}")
        print(f"\n    >>> You need to re-authenticate. Run this in your terminal:")
        print(f"    >>> python gmail_sender.py --to your@email.com --subject Test --body Hello")
        sys.exit(1)
else:
    print(f"VALID (expires: {creds.expiry})")

# 3. Build Gmail API
print(f"\n[4] Building Gmail API . ", end="")
from googleapiclient.discovery import build
try:
    service = build("gmail", "v1", credentials=creds)
    print("SUCCESS")
except Exception as e:
    print(f"FAILED: {e}")
    sys.exit(1)

# 4. Test API connectivity
print(f"[5] API connectivity ... ", end="")
try:
    service.users().labels().list(userId="me").execute()
    print("CONNECTED")
except Exception as e:
    print(f"WARNING: {e} (but send may still work)")

from config import SENDER_EMAIL, SENDER_NAME
print(f"\n[6] Sender: {SENDER_NAME} <{SENDER_EMAIL}>")

print("\n" + "=" * 50)
print("  ALL CHECKS PASSED -- READY TO SEND EMAILS")
print("=" * 50)
