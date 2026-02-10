#!/usr/bin/env python3
"""
process_files.py — Process /Needs_Action files and route them appropriately.

Usage:
    python process_files.py                   # Process all pending items
    python process_files.py --dry-run         # Preview without moving files
    python process_files.py --file EMAIL_x.md # Process a single file

Environment variables (.env):
    VAULT_PATH   Path to Obsidian vault root
    DRY_RUN      true/false
"""

import json
import logging
import os
import re
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("file-processor")

VAULT_PATH = Path(os.getenv("VAULT_PATH", "~/AI_Employee_Vault")).expanduser()
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"

PRIORITY_KEYWORDS = [
    "urgent", "asap", "immediately", "emergency",
    "invoice", "payment", "overdue", "refund",
    "complaint", "unhappy", "cancel",
]


# ── Frontmatter parsing ───────────────────────────────────────────────────────
def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Extract YAML-like frontmatter (key: value) and body from markdown."""
    frontmatter = {}
    body = content
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].splitlines():
                line = line.strip()
                if ": " in line:
                    k, v = line.split(": ", 1)
                    frontmatter[k.strip()] = v.strip()
            body = parts[2].strip()
    return frontmatter, body


# ── Routing logic ─────────────────────────────────────────────────────────────
def requires_approval(fm: dict, body: str) -> tuple[bool, str]:
    """Determine if item needs human approval. Returns (bool, reason)."""
    item_type = fm.get("type", "unknown")
    subject = fm.get("subject", "")
    sender = fm.get("from", "")
    text = f"{subject} {body}".lower()

    # Safety rules — always require approval
    if item_type == "payment":
        return True, "All payments require human approval"

    if item_type == "email":
        # New/unknown sender
        if not sender or "unknown" in sender.lower():
            return True, "Unknown sender — requires verification"
        # High-priority keyword in subject
        if any(kw in text for kw in PRIORITY_KEYWORDS):
            return True, f"Priority keyword detected in email"

    if item_type == "whatsapp":
        if any(kw in text for kw in PRIORITY_KEYWORDS):
            return True, f"Priority keyword detected in WhatsApp message"

    if item_type == "file_drop":
        return True, "File drop — review required before processing"

    return False, ""


# ── File writers ──────────────────────────────────────────────────────────────
def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def expires_iso(hours: int = 24) -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%SZ")


def slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[\s_-]+", "_", text).strip("_")[:40]


def write_plan(source_file: Path, fm: dict, body: str, needs_approval: bool, reason: str):
    plans_dir = VAULT_PATH / "Plans"
    plans_dir.mkdir(parents=True, exist_ok=True)

    slug = slugify(fm.get("subject", fm.get("type", "item")))
    plan_path = plans_dir / f"PLAN_{slug}.md"

    # Avoid overwrite
    counter = 2
    while plan_path.exists():
        plan_path = plans_dir / f"PLAN_{slug}_v{counter}.md"
        counter += 1

    next_action = f"Route to /Pending_Approval: {reason}" if needs_approval else "Review and archive"

    content = f"""---
type: plan
source_file: {source_file.name}
created: {now_iso()}
status: {"pending_approval" if needs_approval else "pending"}
requires_approval: {"true" if needs_approval else "false"}
priority: {fm.get("priority", "medium")}
---

# Plan: {fm.get("subject", fm.get("type", "Item"))}

## Objective
Process {fm.get("type", "item")} from {fm.get("from", "unknown source")}.

## Context
- **Source**: {fm.get("type", "unknown")} from {fm.get("from", "unknown")}
- **Received**: {fm.get("received", now_iso())}
- **Priority**: {fm.get("priority", "medium")}

## Steps
- [x] Received and triaged by AI Employee
- [x] Company Handbook rules applied
- [ ] {next_action}

## Approval Required
{"⚠️ Yes — " + reason if needs_approval else "No — item can be processed automatically"}

---
*Plan created by AI Employee · {now_iso()}*
"""
    if DRY_RUN:
        logger.info(f"[DRY RUN] Would write plan: {plan_path.name}")
    else:
        plan_path.write_text(content, encoding="utf-8")
        logger.info(f"Created plan: {plan_path.name}")

    return plan_path


def write_approval(source_file: Path, fm: dict, reason: str):
    approval_dir = VAULT_PATH / "Pending_Approval"
    approval_dir.mkdir(parents=True, exist_ok=True)

    slug = slugify(fm.get("subject", fm.get("type", "action")))
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    approval_path = approval_dir / f"APPROVAL_{slug}_{date_str}.md"

    content = f"""---
type: approval_request
action: {fm.get("type", "unknown")}
source_file: {source_file.name}
created: {now_iso()}
expires: {expires_iso(24)}
status: pending
priority: {fm.get("priority", "medium")}
---

# Approval Required: {fm.get("subject", fm.get("type", "Action"))}

## What Needs Approval
{reason}

## Details
| Field | Value |
|-------|-------|
| Action | {fm.get("type", "unknown")} |
| From | {fm.get("from", "unknown")} |
| Subject | {fm.get("subject", "—")} |
| Received | {fm.get("received", now_iso())} |

## To Approve
Move this file to `/Approved/` folder.

## To Reject
Move this file to `/Rejected/` folder.

---
*Created by AI Employee · Expires: {expires_iso(24)}*
"""
    if DRY_RUN:
        logger.info(f"[DRY RUN] Would write approval: {approval_path.name}")
    else:
        approval_path.write_text(content, encoding="utf-8")
        logger.info(f"Created approval request: {approval_path.name}")


def move_to_done(source_file: Path):
    done_dir = VAULT_PATH / "Done"
    done_dir.mkdir(parents=True, exist_ok=True)
    dest = done_dir / source_file.name
    if DRY_RUN:
        logger.info(f"[DRY RUN] Would move to Done: {source_file.name}")
    else:
        shutil.move(str(source_file), str(dest))
        logger.info(f"Moved to Done: {source_file.name}")


# ── Dashboard update ──────────────────────────────────────────────────────────
def update_dashboard(processed: list[str]):
    dashboard = VAULT_PATH / "Dashboard.md"
    if not dashboard.exists():
        return

    content = dashboard.read_text(encoding="utf-8")
    timestamp = now_iso()
    new_entries = "\n".join(f"- [{timestamp}] {entry}" for entry in processed)

    if "## Recent Activity" in content:
        content = content.replace(
            "## Recent Activity\n",
            f"## Recent Activity\n{new_entries}\n"
        )
    else:
        content += f"\n\n## Recent Activity\n{new_entries}\n"

    if DRY_RUN:
        logger.info("[DRY RUN] Would update Dashboard.md")
    else:
        dashboard.write_text(content, encoding="utf-8")
        logger.info("Dashboard.md updated")


# ── Main processor ────────────────────────────────────────────────────────────
def process_file(source_file: Path) -> str:
    """Process a single action file. Returns activity log entry."""
    content = source_file.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(content)

    needs_appr, reason = requires_approval(fm, body)
    write_plan(source_file, fm, body, needs_appr, reason)

    if needs_appr:
        write_approval(source_file, fm, reason)

    move_to_done(source_file)

    action = f"Routed to Pending_Approval: {source_file.name}" if needs_appr else f"Processed: {source_file.name}"
    return action


def run_processor(single_file: str = None):
    if DRY_RUN:
        logger.info("⚠️  DRY RUN mode — no files will be moved or written")

    needs_action = VAULT_PATH / "Needs_Action"
    if not needs_action.exists():
        logger.error(f"Needs_Action folder not found at {needs_action}")
        logger.error("Run the vault-setup skill first.")
        sys.exit(1)

    if single_file:
        files = [needs_action / single_file]
    else:
        files = sorted(needs_action.glob("*.md"))

    if not files:
        logger.info("No items in /Needs_Action — nothing to process")
        return

    logger.info(f"Processing {len(files)} item(s)...")
    activity_log = []

    for f in files:
        if not f.exists():
            logger.warning(f"File not found: {f}")
            continue
        try:
            entry = process_file(f)
            activity_log.append(entry)
        except Exception as e:
            logger.error(f"Error processing {f.name}: {e}")

    update_dashboard(activity_log)
    logger.info(f"✅ Done. Processed {len(activity_log)} item(s).")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AI Employee File Processor")
    parser.add_argument("--dry-run", action="store_true", help="Preview without changes")
    parser.add_argument("--file", help="Process a single file by name")
    args = parser.parse_args()
    if args.dry_run:
        DRY_RUN = True
    run_processor(single_file=args.file)
