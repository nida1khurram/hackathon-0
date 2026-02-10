# Dashboard Schema

## Required Sections (in order)

```markdown
---
type: dashboard
last_updated: ISO-8601
---

# 🤖 AI Employee Dashboard — {BUSINESS}

## 📊 Status          ← Live metrics table
## 🔔 Alerts          ← High-priority flags
## 📋 Recent Activity ← Last 10 log entries (newest first)
## 📁 Quick Links     ← Static navigation links
## 📈 Weekly Summary  ← Revenue and task table
```

## Status Table Fields

| Field | Source | Format |
|-------|--------|--------|
| Last updated | Current timestamp | ISO-8601 |
| Pending actions | Count of `/Needs_Action/*.md` | Integer |
| Items in Needs_Action | Same | Integer |
| Awaiting approval | Count of `/Pending_Approval/*.md` | Integer |
| Completed today | Count of `/Done/*.md` modified today | Integer |
| MTD Revenue | From `Business_Goals.md` | `$X,XXX.XX` |
| Monthly target | From `Business_Goals.md` | `$X,XXX.XX` |
| Agent health | Process check | ✅ Online / ❌ Offline |

## Alert Conditions

| Condition | Alert Text |
|-----------|-----------|
| Pending approval > 24h | `⚠️ APPROVAL_*.md pending over 24 hours` |
| Needs_Action > 12h | `⚠️ EMAIL_*.md unprocessed over 12 hours` |
| MTD < 50% at mid-month | `⚠️ Revenue behind target` |
| No activity in 48h | `⚠️ No agent activity detected` |

## Recent Activity Format

```markdown
- [2026-01-07T10:45:00Z] Processed: EMAIL_18f3a2b.md → Plans/
- [2026-01-07T10:46:00Z] Routed to Pending_Approval: WHATSAPP_client_a.md
- [2026-01-07T10:47:00Z] Dashboard refreshed
```

Limit to last 20 entries. Older entries are in `/Logs/`.
