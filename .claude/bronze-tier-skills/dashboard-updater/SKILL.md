---
name: dashboard-updater
description: |
  Reads the Obsidian vault state and rewrites Dashboard.md with a live summary
  of pending actions, recent activity, revenue metrics, alerts, and agent health.
  Implements the single-writer rule to prevent concurrent dashboard corruption.
  This skill should be used when users want to refresh the Dashboard.md summary,
  update metrics after processing tasks, generate the morning status snapshot, or
  verify the AI Employee system health at a glance.
allowed-tools: Read, Write, Glob, Bash
---

# Dashboard Updater

Rewrite Dashboard.md with a live snapshot of vault state and business metrics.

## What This Skill Does

- Counts items in each vault folder (`/Needs_Action`, `/Pending_Approval`, `/Done`, `/Plans`)
- Reads `Business_Goals.md` for revenue targets and MTD figures
- Reads `/Accounting/Current_Month.md` if present for financial data
- Scans recent `/Logs/*.json` for activity
- Rewrites `Dashboard.md` with fresh metrics
- Appends to Recent Activity log (does not delete history)

## What This Skill Does NOT Do

- Modify any files other than `Dashboard.md`
- Generate CEO Briefings (handled by `dashboard-updater` variant in Gold tier)
- Process or route items (handled by file-processor skill)
- Send notifications

---

## Before Implementation

Gather context before updating:

| Source | Gather |
|--------|--------|
| **Codebase** | List all vault folders, count files in each |
| **Conversation** | Any specific metrics user wants highlighted |
| **Skill References** | Dashboard schema from `references/dashboard-schema.md` |

No questions needed for a standard refresh. Only ask if user wants custom sections.

---

## Update Workflow

```
Acquire write lock (create .dashboard_lock)
        ↓
Read vault folder counts
        ↓
Read Business_Goals.md (revenue target + MTD)
        ↓
Read Accounting/Current_Month.md (if exists)
        ↓
Read recent Logs/ entries (last 10)
        ↓
Detect alerts (overdue, high-priority pending)
        ↓
Write Dashboard.md
        ↓
Release lock (delete .dashboard_lock)
```

### Step 1 – Write Lock

Before writing, create `{vault_path}/.dashboard_lock`.
If lock exists and is older than 5 minutes → stale lock, remove and proceed.
If lock exists and is fresh → wait 10 seconds and retry once.

```python
lock_file = vault_path / ".dashboard_lock"
if lock_file.exists() and (time.time() - lock_file.stat().st_mtime) < 300:
    time.sleep(10)  # wait for other writer
lock_file.touch()
```

### Step 2 – Count Folder Items

```python
counts = {
    "needs_action": len(list((vault / "Needs_Action").glob("*.md"))),
    "pending_approval": len(list((vault / "Pending_Approval").glob("*.md"))),
    "plans": len(list((vault / "Plans").glob("*.md"))),
    "done_today": len([f for f in (vault / "Done").glob("*.md")
                       if f.stat().st_mtime > today_start]),
}
```

### Step 3 – Revenue Metrics

Read `Business_Goals.md`. Extract:
- `Monthly goal` line → target amount
- `Current MTD` line → current amount

### Step 4 – Alert Detection

Flag as alert if:
- Any file in `/Pending_Approval` older than 24 hours
- Any file in `/Needs_Action` older than 12 hours
- Revenue MTD below 50% of monthly goal after mid-month

### Step 5 – Write Dashboard

Use the template from `assets/dashboard-output.md`.
Preserve any custom sections the user has added below the standard sections.

### Step 6 – Release Lock

```python
lock_file.unlink(missing_ok=True)
```

---

## Error Handling

| Error | Action |
|-------|--------|
| `Business_Goals.md` missing | Use `—` for revenue metrics, continue |
| `/Accounting` missing | Skip financial section |
| Dashboard write fails | Release lock, log error, do NOT corrupt existing file |
| Lock file stale | Log warning, remove lock, proceed |

---

## Anti-Patterns to Avoid

- Never truncate `Dashboard.md` before writing — always read first, then overwrite
- Never let two processes write simultaneously — always use the lock file
- Never delete the Recent Activity history — only prepend new entries
- Never hardcode timezone — use UTC for all timestamps

---

## Reference Files

| File | When to Read |
|------|--------------|
| `references/dashboard-schema.md` | Section structure and field definitions |
| `references/metrics-extraction.md` | How to parse Business_Goals.md and logs |
| `assets/dashboard-output.md` | Full Dashboard.md output template |
| `scripts/update_dashboard.py` | Automated dashboard update script |
