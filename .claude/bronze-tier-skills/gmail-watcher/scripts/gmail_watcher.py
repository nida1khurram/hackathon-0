#!/usr/bin/env python3
"""
gmail_watcher.py — Monitor Gmail and write action files to Obsidian vault.

Usage:
    python gmail_watcher.py              # Start polling
    python gmail_watcher.py --setup      # First-time OAuth setup
    python gmail_watcher.py --dry-run    # Preview without writing files

Environment variables (.env):
    VAULT_PATH                  Path to Obsidian vault root
    GMAIL_CREDENTIALS_PATH      Path to credentials.json (OAuth client)
    GMAIL_TOKEN_PATH            Path to token.json (saved tokens)
    GMAIL_POLL_INTERVAL         Seconds between polls (default: 120)
    GMAIL_QUERY                 Gmail search query (default: is:unread is:important)
    DRY_RUN                     true/false (default: false)
"""

import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("gmail-watcher")

# ── Config ───────────────────────────────────────────────────────────────────
VAULT_PATH = Path(os.getenv("VAULT_PATH", "~/AI_Employee_Vault")).expanduser()
CREDENTIALS_PATH = Path(os.getenv("GMAIL_CREDENTIALS_PATH", "credentials.json")).expanduser()
TOKEN_PATH = Path(os.getenv("GMAIL_TOKEN_PATH", "token.json")).expanduser()
POLL_INTERVAL = int(os.getenv("GMAIL_POLL_INTERVAL", "120"))
GMAIL_QUERY = os.getenv("GMAIL_QUERY", "is:unread is:important")
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"

PRIORITY_KEYWORDS = [
    "urgent", "asap", "immediately", "emergency",
    "invoice", "payment", "overdue", "refund",
    "complaint", "unhappy", "cancel",
]

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


# ── OAuth helpers ─────────────────────────────────────────────────────────────
def get_gmail_service():
    """Authenticate and return Gmail API service."""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError:
        logger.error("Missing dependencies. Run: pip install google-auth google-auth-oauthlib google-api-python-client")
        sys.exit(1)

    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Refreshing expired token...")
            creds.refresh(Request())
        else:
            if not CREDENTIALS_PATH.exists():
                logger.error(f"credentials.json not found at {CREDENTIALS_PATH}")
                logger.error("Run: python gmail_watcher.py --setup")
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
            creds = flow.run_local_server(port=8080)

        TOKEN_PATH.write_text(creds.to_json())
        logger.info(f"Token saved to {TOKEN_PATH}")

    return build("gmail", "v1", credentials=creds)


def run_oauth_setup():
    """Interactive first-time OAuth setup."""
    logger.info("Starting OAuth setup flow...")
    get_gmail_service()
    logger.info("✅ OAuth setup complete! token.json saved.")
    logger.info("You can now run the watcher: python gmail_watcher.py")


# ── Priority detection ────────────────────────────────────────────────────────
def detect_priority(text: str) -> str:
    text_lower = text.lower()
    return "high" if any(kw in text_lower for kw in PRIORITY_KEYWORDS) else "medium"


# ── Action file writer ────────────────────────────────────────────────────────
def create_action_file(message: dict, headers: dict, snippet: str, label_ids: list) -> Path:
    """Write a structured .md file to /Needs_Action."""
    needs_action = VAULT_PATH / "Needs_Action"
    needs_action.mkdir(parents=True, exist_ok=True)

    msg_id = message["id"]
    filepath = needs_action / f"EMAIL_{msg_id}.md"

    if filepath.exists():
        logger.debug(f"Already exists, skipping: {filepath.name}")
        return filepath

    priority = detect_priority(f"{headers.get('Subject', '')} {snippet}")
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    labels_str = json.dumps(label_ids)

    content = f"""---
type: email
from: {headers.get('From', 'Unknown')}
subject: {headers.get('Subject', 'No Subject')}
received: {timestamp}
message_id: {msg_id}
priority: {priority}
status: pending
labels: {labels_str}
---

## Email Summary
{snippet}

## Suggested Actions
- [ ] Review and draft reply
- [ ] Forward to relevant party
- [ ] Archive after processing
"""

    if DRY_RUN:
        logger.info(f"[DRY RUN] Would write: {filepath}")
        logger.info(f"  From: {headers.get('From')} | Subject: {headers.get('Subject')} | Priority: {priority}")
    else:
        filepath.write_text(content, encoding="utf-8")
        logger.info(f"Created: {filepath.name} (priority={priority})")

    return filepath


# ── Main polling loop ─────────────────────────────────────────────────────────
def poll_once(service, processed_ids: set) -> int:
    """Poll Gmail once, return count of new files created."""
    try:
        result = service.users().messages().list(userId="me", q=GMAIL_QUERY).execute()
        messages = result.get("messages", [])
    except Exception as e:
        logger.error(f"Gmail API error: {e}")
        return 0

    new_count = 0
    for msg_stub in messages:
        msg_id = msg_stub["id"]
        if msg_id in processed_ids:
            continue

        try:
            msg = service.users().messages().get(userId="me", id=msg_id).execute()
        except Exception as e:
            logger.warning(f"Could not fetch message {msg_id}: {e}")
            continue

        headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
        snippet = msg.get("snippet", "")
        label_ids = msg.get("labelIds", [])

        create_action_file(msg_stub, headers, snippet, label_ids)
        processed_ids.add(msg_id)
        new_count += 1

    return new_count


def run_watcher():
    """Main daemon loop."""
    if DRY_RUN:
        logger.info("⚠️  DRY RUN mode enabled — no files will be written")

    logger.info(f"Starting Gmail Watcher | vault={VAULT_PATH} | interval={POLL_INTERVAL}s | query='{GMAIL_QUERY}'")

    if not VAULT_PATH.exists():
        logger.error(f"Vault path not found: {VAULT_PATH}")
        logger.error("Run the vault-setup skill first.")
        sys.exit(1)

    service = get_gmail_service()
    processed_ids: set = set()

    while True:
        try:
            count = poll_once(service, processed_ids)
            if count > 0:
                logger.info(f"Processed {count} new message(s)")
            else:
                logger.debug("No new messages")
        except KeyboardInterrupt:
            logger.info("Watcher stopped by user")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e}")

        time.sleep(POLL_INTERVAL)


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AI Employee Gmail Watcher")
    parser.add_argument("--setup", action="store_true", help="Run OAuth setup flow")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    args = parser.parse_args()

    if args.dry_run:
        DRY_RUN = True

    if args.setup:
        run_oauth_setup()
    else:
        run_watcher()
