# Shopify CRO Outreach Agent

> An autonomous Python agent that audits Shopify stores, generates Neo-Brutalist PDF reports, and sends personalized cold outreach emails via Gmail.

---

## 📁 Project Structure

```
cold email automation/
├── main.py                   # Orchestrator (run this)
├── config.py                 # All settings & paths
├── csv_processor.py          # CSV loading, validation, tracking columns
├── store_auditor.py          # 9-category Shopify CRO audit engine
├── screenshot_capture.py     # Playwright headless screenshots
├── pdf_generator.py          # ReportLab Neo-Brutalist PDF
├── email_composer.py         # Email personalization engine
├── gmail_sender.py           # Gmail API OAuth2 sender
├── tracking.py               # CSV result tracking + summary
├── templates/
│   └── email_template.txt    # Base email template
├── credentials/              # Place your client_secret.json here
├── output/
│   ├── pdfs/                 # Generated audit PDFs
│   └── processed_leads.csv   # Updated tracking CSV
├── logs/                     # Agent run logs
├── sample_leads.csv          # Example CSV for testing
└── requirements.txt
```

---

## ⚙️ Setup

### 1. Python Version
Requires **Python 3.11+**

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install Playwright Browser
```bash
playwright install chromium
```

### 4. Gmail OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable the **Gmail API**: APIs & Services → Enable APIs → Gmail API → Enable
4. Create **OAuth 2.0 Credentials**:
   - APIs & Services → Credentials → Create Credentials → OAuth Client ID
   - Application type: **Desktop App**
   - Name: anything (e.g., "CRO Outreach Agent")
5. Download the JSON file
6. Rename it to **`client_secret.json`** and place it in:
   ```
   credentials/client_secret.json
   ```

> **Note:** On first run, a browser window will open asking you to authorize Gmail access. After approval, a `token.json` is saved automatically and reused on future runs.

---

## 📋 Prepare Your CSV

Your input CSV must have at minimum:

| Column | Required | Description |
|--------|----------|-------------|
| `store_url` | ✅ | Full Shopify store URL |
| `email` | ✅ | Contact email address |
| `store_name` | Optional | Store display name (auto-derived from URL if missing) |
| `niche` | Optional | Product niche (e.g., footwear, skincare) |
| `notes` | Optional | Internal notes |

See `sample_leads.csv` for reference.

---

## 🚀 Running the Agent

### Full Run (audit + PDF + send emails)
```bash
python main.py --csv your_leads.csv
```

### Dry Run (audit + PDF only, no emails sent)
```bash
python main.py --csv your_leads.csv --dry-run
```

### Test Individual Modules

```bash
# Test CSV validation
python csv_processor.py --csv sample_leads.csv

# Test store audit
python store_auditor.py --url https://allbirds.com

# Test PDF generation (uses dummy data)
python pdf_generator.py --test

# Test screenshot capture
python screenshot_capture.py --url https://allbirds.com --name Allbirds

# Test email compose
python email_composer.py --test

# Test Gmail send (single email)
python gmail_sender.py --to your@email.com --subject "Test" --body "Hello"
```

---

## 📊 Output Files

| File | Description |
|------|-------------|
| `output/processed_leads.csv` | Lead list with tracking columns filled in |
| `output/pdfs/<StoreName>_CRO_Audit.pdf` | Generated audit PDF |
| `output/summary_report.txt` | Final run summary |
| `logs/agent_<timestamp>.log` | Detailed run logs |

---

## 🛑 Outreach Limit

The agent **automatically stops** after **100 successfully sent emails**. This is controlled by `MAX_EMAILS` in `config.py`. Change it to adjust the limit.

---

## ⚠️ Important Notes

- **Rate limiting**: The agent waits 10 seconds between sends to avoid Gmail rate limits.
- **Retries**: Failed sends are retried up to 2 times before being marked as failed.
- **Resilience**: Any single failure (audit, screenshot, PDF, email) is logged and the agent continues to the next lead.
- **Resume**: If you stop and restart, already-sent leads (marked `email_success = YES`) are automatically skipped.

---

## 🔧 Configuration

Edit `config.py` to change:
- `MAX_EMAILS` — stop after N successful sends (default: 100)
- `RETRY_LIMIT` — send retries (default: 2)
- `SEND_DELAY` — seconds between sends (default: 10)
- `SENDER_EMAIL` / `SENDER_NAME` — your email signature details

---

## 👤 Author

**Pranav Kashmire** — Shopify Developer  
Email: pranav.kashmire09@gmail.com
