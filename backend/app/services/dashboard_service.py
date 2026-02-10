import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

from app.config import settings
from app.models.dashboard import DashboardMetrics
from app.services.vault_service import DASHBOARD_TEMPLATE


def _count_md_files(folder: Path) -> int:
    """Count .md files in a folder."""
    if not folder.exists():
        return 0
    return len(list(folder.glob("*.md")))


def _count_today_done() -> int:
    """Count files in Done/ that were modified today (UTC)."""
    done_dir = settings.vault_dir / "Done"
    if not done_dir.exists():
        return 0

    today = datetime.now(timezone.utc).date()
    count = 0
    for f in done_dir.glob("*.md"):
        mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc).date()
        if mtime == today:
            count += 1
    return count


def _extract_revenue() -> tuple[str, str]:
    """Extract MTD revenue and monthly target from Business_Goals.md."""
    goals_path = settings.vault_dir / "Business_Goals.md"
    mtd_revenue = "$0.00"
    monthly_target = "$5,000.00"

    if not goals_path.exists():
        return mtd_revenue, monthly_target

    content = goals_path.read_text(encoding="utf-8")

    # Look for the revenue table row: | This Month | $X | $Y | ... |
    match = re.search(
        r"\|\s*This Month\s*\|\s*(\$[\d,.]+)\s*\|\s*(\$[\d,.]+)\s*\|",
        content,
    )
    if match:
        monthly_target = match.group(1)
        mtd_revenue = match.group(2)

    return mtd_revenue, monthly_target


def _detect_alerts() -> list[str]:
    """Detect alert conditions in the vault."""
    alerts: list[str] = []
    now = datetime.now(timezone.utc)

    # Check for approvals pending > 24h
    approval_dir = settings.vault_dir / "Pending_Approval"
    if approval_dir.exists():
        for f in approval_dir.glob("*.md"):
            mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
            if now - mtime > timedelta(hours=24):
                alerts.append(f"Approval pending > 24h: {f.name}")

    # Check for needs_action items > 12h
    needs_action_dir = settings.vault_dir / "Needs_Action"
    if needs_action_dir.exists():
        for f in needs_action_dir.glob("*.md"):
            mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
            if now - mtime > timedelta(hours=12):
                alerts.append(f"Needs action > 12h: {f.name}")

    return alerts


def _get_recent_activity() -> list[str]:
    """Get recent activity from Done and Approved folders."""
    activity: list[str] = []

    for folder_name in ["Done", "Approved", "Rejected"]:
        folder = settings.vault_dir / folder_name
        if not folder.exists():
            continue
        files = sorted(folder.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)
        for f in files[:5]:
            mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
            time_str = mtime.strftime("%Y-%m-%d %H:%M UTC")
            activity.append(f"[{folder_name}] {f.stem} - {time_str}")

    # Sort by most recent and limit
    activity.sort(reverse=True)
    return activity[:10]


def get_metrics() -> DashboardMetrics:
    """Compute current dashboard metrics from vault state."""
    vault = settings.vault_dir

    needs_action = _count_md_files(vault / "Needs_Action")
    pending_approval = _count_md_files(vault / "Pending_Approval")
    done_today = _count_today_done()
    active_plans = _count_md_files(vault / "Plans")
    mtd_revenue, monthly_target = _extract_revenue()
    alerts = _detect_alerts()
    recent_activity = _get_recent_activity()

    return DashboardMetrics(
        needs_action=needs_action,
        pending_approval=pending_approval,
        done_today=done_today,
        active_plans=active_plans,
        mtd_revenue=mtd_revenue,
        monthly_target=monthly_target,
        alerts=alerts if alerts else ["No alerts. All clear."],
        recent_activity=recent_activity if recent_activity else ["No activity yet."],
        agent_health="Online",
    )


def refresh_dashboard() -> str:
    """Write an updated Dashboard.md to the vault root."""
    vault = settings.vault_dir
    dashboard_path = vault / "Dashboard.md"

    metrics = get_metrics()
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    alerts_text = "\n".join(f"- {a}" for a in metrics.alerts)
    activity_text = "\n".join(f"- {a}" for a in metrics.recent_activity)

    content = f"""\
---
type: dashboard
last_updated: {timestamp}
---

# AI Employee Dashboard - {settings.BUSINESS}

## Status

| Metric | Value |
|--------|-------|
| Last updated | {timestamp} |
| Pending actions | {metrics.needs_action} |
| Awaiting approval | {metrics.pending_approval} |
| Completed today | {metrics.done_today} |
| Active plans | {metrics.active_plans} |
| MTD Revenue | {metrics.mtd_revenue} |
| Monthly Target | {metrics.monthly_target} |
| Agent health | {metrics.agent_health} |

## Alerts

{alerts_text}

## Recent Activity

{activity_text}
"""
    dashboard_path.write_text(content, encoding="utf-8")
    return f"Dashboard refreshed at {timestamp}"
