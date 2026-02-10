import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

from app.config import settings
from app.models.action_item import ActionItem, ProcessResult


# Priority keywords that trigger high-priority routing
PRIORITY_KEYWORDS = [
    "urgent", "asap", "immediately", "emergency",
    "invoice", "payment", "overdue", "refund",
    "complaint", "unhappy", "cancel",
]

PRIORITY_ORDER = {"high": 0, "medium": 1, "normal": 2, "low": 3}


def _parse_frontmatter(text: str) -> dict[str, str]:
    """Parse YAML-like frontmatter delimited by --- lines."""
    meta: dict[str, str] = {}
    lines = text.strip().splitlines()
    if not lines or lines[0].strip() != "---":
        return meta

    end_idx = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break

    if end_idx == -1:
        return meta

    for line in lines[1:end_idx]:
        if ":" in line:
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip()

    return meta


def _get_body(text: str) -> str:
    """Return everything after the frontmatter block."""
    lines = text.strip().splitlines()
    if not lines or lines[0].strip() != "---":
        return text

    end_idx = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break

    if end_idx == -1:
        return text

    return "\n".join(lines[end_idx + 1 :]).strip()


def _detect_priority(subject: str, body: str) -> str:
    """Check subject and body for priority keywords."""
    combined = (subject + " " + body).lower()
    for kw in PRIORITY_KEYWORDS:
        if kw in combined:
            return "high"
    return "normal"


def _needs_approval(item_type: str, priority: str, subject: str, body: str) -> bool:
    """Determine whether an action item requires owner approval."""
    # Payment types always need approval
    if item_type == "payment":
        return True
    # Emails with priority keywords need approval
    if item_type == "email":
        combined = (subject + " " + body).lower()
        for kw in PRIORITY_KEYWORDS:
            if kw in combined:
                return True
    return False


def get_action_items() -> list[ActionItem]:
    """Read all .md files in Needs_Action and return parsed ActionItem list."""
    needs_action_dir = settings.vault_dir / "Needs_Action"
    if not needs_action_dir.exists():
        return []

    items: list[ActionItem] = []
    for filepath in sorted(needs_action_dir.glob("*.md")):
        text = filepath.read_text(encoding="utf-8")
        meta = _parse_frontmatter(text)
        body = _get_body(text)

        subject = meta.get("subject", filepath.stem)
        item_type = meta.get("type", "unknown")
        priority = meta.get("priority", _detect_priority(subject, body))

        item = ActionItem(
            id=meta.get("id", uuid.uuid4().hex[:8]),
            filename=filepath.name,
            type=item_type,
            sender=meta.get("from", meta.get("sender", "unknown")),
            subject=subject,
            priority=priority,
            received=meta.get("received", meta.get("date", "")),
            status=meta.get("status", "needs_action"),
            snippet=body[:200] if body else "",
        )
        items.append(item)

    # Sort by priority: high first
    items.sort(key=lambda x: PRIORITY_ORDER.get(x.priority, 99))
    return items


def _write_plan(item: ActionItem, body: str) -> str:
    """Write a plan file to the Plans folder. Returns the plan filename."""
    plans_dir = settings.vault_dir / "Plans"
    plans_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    plan_filename = f"PLAN_{item.id}.md"
    plan_path = plans_dir / plan_filename

    plan_content = f"""\
---
type: plan
source_file: {item.filename}
subject: {item.subject}
priority: {item.priority}
created: {timestamp}
status: active
---

# Plan: {item.subject}

## Source

- **From**: {item.sender}
- **Type**: {item.type}
- **Received**: {item.received}
- **Priority**: {item.priority}

## Summary

{body[:500] if body else 'No details available.'}

## Actions

1. Review the item and determine appropriate response.
2. Execute required actions per handbook rules.
3. Log outcome and update status.
"""
    plan_path.write_text(plan_content, encoding="utf-8")
    return plan_filename


def _write_approval(item: ActionItem, body: str) -> str:
    """Write an approval request to Pending_Approval. Returns the approval filename."""
    approval_dir = settings.vault_dir / "Pending_Approval"
    approval_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    approval_filename = f"APPROVAL_{item.id}.md"
    approval_path = approval_dir / approval_filename

    # Determine reason for approval
    if item.type == "payment":
        reason = "Payment requires owner approval per financial rules."
    else:
        reason = "Contains priority keywords requiring owner review."

    approval_content = f"""\
---
type: approval
id: {item.id}
action: review_and_respond
source_file: {item.filename}
subject: {item.subject}
priority: {item.priority}
created: {timestamp}
expires: 24h
status: pending
reason: {reason}
---

# Approval Required: {item.subject}

## Details

- **From**: {item.sender}
- **Type**: {item.type}
- **Priority**: {item.priority}
- **Received**: {item.received}

## Content

{body[:500] if body else 'No details available.'}

## Reason for Approval

{reason}

## Actions

- **Approve**: Proceed with the recommended action.
- **Reject**: Cancel the action and archive.
"""
    approval_path.write_text(approval_content, encoding="utf-8")
    return approval_filename


def process_item(filename: str) -> str:
    """Process a single item from Needs_Action. Returns a description of what happened."""
    needs_action_dir = settings.vault_dir / "Needs_Action"
    filepath = needs_action_dir / filename

    if not filepath.exists():
        return f"File not found: {filename}"

    text = filepath.read_text(encoding="utf-8")
    meta = _parse_frontmatter(text)
    body = _get_body(text)

    subject = meta.get("subject", filepath.stem)
    item_type = meta.get("type", "unknown")
    priority = meta.get("priority", _detect_priority(subject, body))

    item = ActionItem(
        id=meta.get("id", uuid.uuid4().hex[:8]),
        filename=filename,
        type=item_type,
        sender=meta.get("from", meta.get("sender", "unknown")),
        subject=subject,
        priority=priority,
        received=meta.get("received", meta.get("date", "")),
        status="processing",
        snippet=body[:200] if body else "",
    )

    # Write plan
    plan_file = _write_plan(item, body)

    if _needs_approval(item_type, priority, subject, body):
        # Write approval request and move to In_Progress
        approval_file = _write_approval(item, body)
        in_progress_dir = settings.vault_dir / "In_Progress"
        in_progress_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(filepath), str(in_progress_dir / filename))
        return f"Routed to approval ({approval_file}). Plan: {plan_file}. Moved to In_Progress."
    else:
        # Move directly to Done
        done_dir = settings.vault_dir / "Done"
        done_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(filepath), str(done_dir / filename))
        return f"Completed. Plan: {plan_file}. Moved to Done."


def process_all() -> ProcessResult:
    """Process all items in Needs_Action."""
    needs_action_dir = settings.vault_dir / "Needs_Action"
    if not needs_action_dir.exists():
        return ProcessResult(processed=0, actions=[])

    files = list(needs_action_dir.glob("*.md"))
    actions: list[str] = []

    for filepath in files:
        result = process_item(filepath.name)
        actions.append(f"{filepath.name}: {result}")

    return ProcessResult(processed=len(files), actions=actions)
