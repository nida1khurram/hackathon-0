#!/usr/bin/env python3
"""
update_dashboard.py — Refresh Dashboard.md with live vault metrics.

Usage:
    python update_dashboard.py
    python update_dashboard.py --dry-run

Environment variables (.env):
    VAULT_PATH   Path to Obsidian vault root
    DRY_RUN      true/false
"""

import logging
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("dashboard-updater")

VAULT_PATH = Path(os.getenv("VAULT_PATH", "~/AI_Employee_Vault")).expanduser()
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"
MAX_ACTIVITY_LINES = 20


# ── Helpers ───────────────────────────────────────────────────────────────────
def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def today_start_ts() -> float:
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    return today.timestamp()


def count_md(folder: Path) -> int:
    if not folder.exists():
        return 0
    return len(list(folder.glob("*.md")))


def count_done_today(done_folder: Path) -> int:
    if not done_folder.exists():
        return 0
    ts = today_start_ts()
    return sum(1 for f in done_folder.glob("*.md") if f.stat().st_mtime >= ts)


def oldest_file_age_hours(folder: Path) -> float | None:
    if not folder.exists():
        return None
    files = list(folder.glob("*.md"))
    if not files:
        return None
    oldest_mtime = min(f.stat().st_mtime for f in files)
    return (time.time() - oldest_mtime) / 3600


# ── Revenue extraction ────────────────────────────────────────────────────────
def extract_revenue(goals_path: Path) -> tuple[str, str]:
    """Return (mtd_value, monthly_goal) as formatted strings."""
    if not goals_path.exists():
        return "—", "—"
    content = goals_path.read_text(encoding="utf-8")
    mtd = re.search(r"Current MTD[:\s*]+\$?([\d,]+\.?\d*)", content)
    goal = re.search(r"Monthly goal[:\s*]+\$?([\d,]+\.?\d*)", content)
    mtd_val = f"${mtd.group(1)}" if mtd else "—"
    goal_val = f"${goal.group(1)}" if goal else "—"
    return mtd_val, goal_val


# ── Alert detection ───────────────────────────────────────────────────────────
def build_alerts(counts: dict, vault: Path) -> list[str]:
    alerts = []

    age = oldest_file_age_hours(vault / "Pending_Approval")
    if age and age > 24:
        alerts.append(f"⚠️ Approval request pending over 24 hours — review `/Pending_Approval/`")

    age = oldest_file_age_hours(vault / "Needs_Action")
    if age and age > 12:
        alerts.append(f"⚠️ Items in `/Needs_Action/` unprocessed over 12 hours")

    return alerts


# ── Activity log ──────────────────────────────────────────────────────────────
def extract_recent_activity(existing_dashboard: str) -> list[str]:
    """Extract existing Recent Activity entries from current dashboard."""
    lines = []
    in_section = False
    for line in existing_dashboard.splitlines():
        if line.startswith("## 📋 Recent Activity"):
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section and line.startswith("- ["):
            lines.append(line)
    return lines[:MAX_ACTIVITY_LINES]


# ── Dashboard writer ──────────────────────────────────────────────────────────
def build_dashboard(vault: Path, counts: dict, mtd: str, goal: str,
                    alerts: list[str], recent: list[str], business: str) -> str:
    timestamp = now_iso()
    health = "✅ Online"

    alert_section = "\n".join(alerts) if alerts else "_No alerts. All clear._"

    new_activity = f"- [{timestamp}] Dashboard refreshed — {counts['needs_action']} pending, {counts['pending_approval']} awaiting approval"
    activity_entries = [new_activity] + recent
    activity_section = "\n".join(activity_entries[:MAX_ACTIVITY_LINES])

    return f"""---
type: dashboard
last_updated: {timestamp}
---

# 🤖 AI Employee Dashboard — {business}

> Real-time summary of your Personal AI Employee's activity.

---

## 📊 Status

| Metric | Value |
|--------|-------|
| Last updated | {timestamp} |
| Pending actions | {counts['needs_action']} |
| Items in Needs_Action | {counts['needs_action']} |
| Awaiting approval | {counts['pending_approval']} |
| Completed today | {counts['done_today']} |
| Active plans | {counts['plans']} |
| MTD Revenue | {mtd} |
| Monthly target | {goal} |
| Agent health | {health} |

---

## 🔔 Alerts

{alert_section}

---

## 📋 Recent Activity

{activity_section}

---

## 📁 Quick Links

- [[Company_Handbook]] — Rules of Engagement
- [[Business_Goals]] — Current OKRs and KPIs
- [Needs Action](Needs_Action) — Items awaiting processing
- [Pending Approval](Pending_Approval) — Actions awaiting your review
- [Done](Done) — Completed tasks archive
- [Logs](Logs) — Full audit trail

---
*Managed by AI Employee · {business}*
"""


# ── Lock management ───────────────────────────────────────────────────────────
def acquire_lock(vault: Path) -> Path:
    lock = vault / ".dashboard_lock"
    if lock.exists():
        age = time.time() - lock.stat().st_mtime
        if age < 300:  # 5 minutes
            logger.warning("Lock file exists, waiting 10s...")
            time.sleep(10)
        else:
            logger.warning("Stale lock file found, removing...")
            lock.unlink()
    lock.touch()
    return lock


# ── Main ──────────────────────────────────────────────────────────────────────
def run():
    if DRY_RUN:
        logger.info("⚠️  DRY RUN mode — no files will be written")

    if not VAULT_PATH.exists():
        logger.error(f"Vault not found: {VAULT_PATH}")
        return

    lock = acquire_lock(VAULT_PATH)
    try:
        # Read business name from existing dashboard or default
        dashboard_path = VAULT_PATH / "Dashboard.md"
        business = "My Business"
        existing = ""
        if dashboard_path.exists():
            existing = dashboard_path.read_text(encoding="utf-8")
            match = re.search(r"# 🤖 AI Employee Dashboard — (.+)", existing)
            if match:
                business = match.group(1).strip()

        # Gather metrics
        counts = {
            "needs_action": count_md(VAULT_PATH / "Needs_Action"),
            "pending_approval": count_md(VAULT_PATH / "Pending_Approval"),
            "plans": count_md(VAULT_PATH / "Plans"),
            "done_today": count_done_today(VAULT_PATH / "Done"),
        }

        mtd, goal = extract_revenue(VAULT_PATH / "Business_Goals.md")
        alerts = build_alerts(counts, VAULT_PATH)
        recent = extract_recent_activity(existing) if existing else []

        content = build_dashboard(VAULT_PATH, counts, mtd, goal, alerts, recent, business)

        if DRY_RUN:
            logger.info("[DRY RUN] Dashboard preview:")
            print(content[:800] + "\n... (truncated)")
        else:
            dashboard_path.write_text(content, encoding="utf-8")
            logger.info(f"✅ Dashboard.md updated — {counts['needs_action']} pending, {counts['pending_approval']} awaiting approval")

    finally:
        lock.unlink(missing_ok=True)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AI Employee Dashboard Updater")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.dry_run:
        DRY_RUN = True
    run()
