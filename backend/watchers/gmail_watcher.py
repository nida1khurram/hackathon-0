"""
gmail_watcher.py — Async Gmail poller that writes action files to the vault.

Runs as a background task inside FastAPI's lifespan.
Falls back gracefully if credentials.json is missing.
In DRY_RUN mode, logs what *would* happen without writing files.

Standalone usage:
    python -m watchers.gmail_watcher --setup   # First-time OAuth
    python -m watchers.gmail_watcher            # Start polling (blocking)
"""

import asyncio
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger("gmail-watcher")

PRIORITY_KEYWORDS = [
    "urgent", "asap", "immediately", "emergency",
    "invoice", "payment", "overdue", "refund",
    "complaint", "unhappy", "cancel",
]

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


# ── OAuth helpers ────────────────────────────────────────────────────────────

def _get_gmail_service(credentials_path: Path, token_path: Path):
    """Authenticate and return Gmail API service (sync helper)."""
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Refreshing expired token...")
            creds.refresh(Request())
        else:
            if not credentials_path.exists():
                raise FileNotFoundError(
                    f"credentials.json not found at {credentials_path}. "
                    "Run: python -m watchers.gmail_watcher --setup"
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
            creds = flow.run_local_server(port=8080)

        token_path.write_text(creds.to_json())
        logger.info("Token saved to %s", token_path)

    return build("gmail", "v1", credentials=creds)


# ── Priority detection ───────────────────────────────────────────────────────

def _detect_priority(text: str) -> str:
    text_lower = text.lower()
    return "high" if any(kw in text_lower for kw in PRIORITY_KEYWORDS) else "medium"


# ── Action file writer ───────────────────────────────────────────────────────

def _create_action_file(
    vault_path: Path, message: dict, headers: dict, snippet: str,
    label_ids: list, dry_run: bool,
) -> Path:
    """Write a structured .md file to Needs_Action/."""
    needs_action = vault_path / "Needs_Action"
    needs_action.mkdir(parents=True, exist_ok=True)

    msg_id = message["id"]
    filepath = needs_action / f"EMAIL_{msg_id}.md"

    if filepath.exists():
        logger.debug("Already exists, skipping: %s", filepath.name)
        return filepath

    priority = _detect_priority(f"{headers.get('Subject', '')} {snippet}")
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    content = f"""---
type: email
from: {headers.get('From', 'Unknown')}
subject: {headers.get('Subject', 'No Subject')}
received: {timestamp}
message_id: {msg_id}
priority: {priority}
status: pending
labels: {json.dumps(label_ids)}
---

## Email Summary
{snippet}

## Suggested Actions
- [ ] Review and draft reply
- [ ] Forward to relevant party
- [ ] Archive after processing
"""

    if dry_run:
        logger.info(
            "[DRY RUN] Would write: %s | From: %s | Subject: %s | Priority: %s",
            filepath.name, headers.get("From"), headers.get("Subject"), priority,
        )
    else:
        filepath.write_text(content, encoding="utf-8")
        logger.info("Created: %s (priority=%s)", filepath.name, priority)

    return filepath


# ── Single poll ──────────────────────────────────────────────────────────────

def _poll_once(service, vault_path: Path, query: str, processed_ids: set, dry_run: bool) -> int:
    """Poll Gmail once, return count of new messages processed."""
    try:
        result = service.users().messages().list(userId="me", q=query).execute()
        messages = result.get("messages", [])
    except Exception as e:
        logger.error("Gmail API error: %s", e)
        return 0

    new_count = 0
    for msg_stub in messages:
        msg_id = msg_stub["id"]
        if msg_id in processed_ids:
            continue

        try:
            msg = service.users().messages().get(userId="me", id=msg_id).execute()
        except Exception as e:
            logger.warning("Could not fetch message %s: %s", msg_id, e)
            continue

        headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
        snippet = msg.get("snippet", "")
        label_ids = msg.get("labelIds", [])

        _create_action_file(vault_path, msg_stub, headers, snippet, label_ids, dry_run)
        processed_ids.add(msg_id)
        new_count += 1

    return new_count


# ── Async background task (called from FastAPI lifespan) ─────────────────────

async def run_gmail_watcher_async(
    vault_path: Path,
    credentials_path: Path,
    token_path: Path,
    poll_interval: int,
    query: str,
    dry_run: bool,
):
    """Long-running async task that polls Gmail on an interval."""
    if dry_run:
        logger.info("[Gmail] DRY RUN mode — no files will be written")

    logger.info(
        "[Gmail] Starting | vault=%s | interval=%ds | query='%s'",
        vault_path, poll_interval, query,
    )

    if not vault_path.exists():
        logger.error("[Gmail] Vault path not found: %s", vault_path)
        return

    # Build the service (sync, runs in thread pool)
    loop = asyncio.get_running_loop()
    try:
        service = await loop.run_in_executor(
            None, _get_gmail_service, credentials_path, token_path,
        )
    except FileNotFoundError as e:
        logger.warning("[Gmail] %s — watcher disabled", e)
        return
    except Exception as e:
        logger.error("[Gmail] Auth failed: %s — watcher disabled", e)
        return

    processed_ids: set = set()

    while True:
        try:
            count = await loop.run_in_executor(
                None, _poll_once, service, vault_path, query, processed_ids, dry_run,
            )
            if count > 0:
                logger.info("[Gmail] Processed %d new message(s)", count)
        except asyncio.CancelledError:
            logger.info("[Gmail] Watcher stopped")
            return
        except Exception as e:
            logger.error("[Gmail] Unexpected error: %s", e)

        await asyncio.sleep(poll_interval)


# ── Standalone entry point ───────────────────────────────────────────────────

def _run_oauth_setup(credentials_path: Path, token_path: Path):
    """Interactive first-time OAuth setup."""
    logger.info("Starting OAuth setup flow...")
    _get_gmail_service(credentials_path, token_path)
    logger.info("OAuth setup complete! token.json saved.")
    logger.info("You can now start the server: uvicorn app.main:app --reload")


if __name__ == "__main__":
    import argparse
    from dotenv import load_dotenv
    import os

    load_dotenv()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    creds_path = Path(os.getenv("GMAIL_CREDENTIALS_PATH", "credentials.json")).expanduser()
    tok_path = Path(os.getenv("GMAIL_TOKEN_PATH", "token.json")).expanduser()

    parser = argparse.ArgumentParser(description="AI Employee Gmail Watcher")
    parser.add_argument("--setup", action="store_true", help="Run OAuth setup flow")
    args = parser.parse_args()

    if args.setup:
        _run_oauth_setup(creds_path, tok_path)
    else:
        vault = Path(os.getenv("VAULT_PATH", "../vault")).resolve()
        interval = int(os.getenv("GMAIL_POLL_INTERVAL", "120"))
        query = os.getenv("GMAIL_QUERY", "is:unread is:important")
        dry_run = os.getenv("DRY_RUN", "true").lower() == "true"
        asyncio.run(run_gmail_watcher_async(vault, creds_path, tok_path, interval, query, dry_run))
