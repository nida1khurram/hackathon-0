---
name: gmail-watcher
description: |
  Monitors a Gmail inbox for important or unread messages and writes structured
  action files into an Obsidian vault's /Needs_Action folder. Supports Gmail API
  (OAuth2) mode and filesystem drop mode for local file monitoring.
  This skill should be used when users want to set up email monitoring for their
  AI Employee, configure Gmail OAuth credentials, start/stop the watcher process,
  or troubleshoot Gmail watcher failures.
allowed-tools: Read, Write, Bash, Glob
---

# Gmail Watcher

Monitor Gmail and write structured action files to the Obsidian vault.

## What This Skill Does

- Polls Gmail for unread/important messages on a configurable interval
- Writes one `EMAIL_<id>.md` file per message into `/Needs_Action`
- Tracks processed message IDs to prevent duplicate files
- Supports both Gmail API mode and filesystem drop mode
- Includes dry-run mode for safe development/testing

## What This Skill Does NOT Do

- Send emails (handled by email-mcp at Silver tier)
- Process or reply to emails (handled by file-processor skill)
- Handle OAuth consent flow automatically (user must run setup once)
- Monitor multiple Gmail accounts simultaneously

---

## Before Implementation

Gather context before configuring:

| Source | Gather |
|--------|--------|
| **Conversation** | Vault path, Gmail address, desired poll interval |
| **Codebase** | Existing watcher scripts, `.env` file location |
| **User Guidelines** | Priority keywords to filter on, business hours rules |

Ask only: vault path and Gmail address. Everything else is defaulted below.

---

## Setup Workflow

```
Install dependencies
        ↓
Run OAuth setup (once)
        ↓
Configure .env
        ↓
Test with --dry-run
        ↓
Start watcher (via PM2 or direct)
```

### Step 1 – Install Dependencies

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client python-dotenv
```

### Step 2 – OAuth Setup (One-Time)

1. Go to Google Cloud Console → Enable Gmail API
2. Create OAuth 2.0 credentials → Download as `credentials.json`
3. Place `credentials.json` in your project root (NOT in the vault)
4. Run once to authorize:

```bash
python scripts/gmail_watcher.py --setup
```

This opens a browser for consent and saves `token.json` (also outside vault).

### Step 3 – Configure .env

```bash
VAULT_PATH=/path/to/AI_Employee_Vault
GMAIL_CREDENTIALS_PATH=/path/to/credentials.json
GMAIL_TOKEN_PATH=/path/to/token.json
GMAIL_POLL_INTERVAL=120          # seconds between polls
GMAIL_QUERY=is:unread is:important
DRY_RUN=false
```

### Step 4 – Test

```bash
DRY_RUN=true python scripts/gmail_watcher.py
```

Verify `.md` files appear in `/Needs_Action` after a poll cycle.

### Step 5 – Start with PM2 (Recommended)

```bash
npm install -g pm2
pm2 start scripts/gmail_watcher.py --interpreter python3 --name gmail-watcher
pm2 save && pm2 startup
```

Or run directly: `python scripts/gmail_watcher.py`

---

## Output File Schema

Each message creates `EMAIL_<message_id>.md` in `/Needs_Action`:

```yaml
---
type: email
from: sender@example.com
subject: Subject line here
received: 2026-01-07T10:30:00Z
message_id: 18f3a2b4c5d6e7f8
priority: high
status: pending
labels: [INBOX, IMPORTANT]
---

## Email Summary
<snippet from Gmail API>

## Suggested Actions
- [ ] Review and draft reply
- [ ] Forward to relevant party
- [ ] Archive after processing
```

---

## Priority Detection

Automatically sets `priority: high` when subject/snippet contains:
- urgent, asap, immediately, emergency
- invoice, payment, overdue, refund
- complaint, unhappy, cancel

Otherwise: `priority: medium`

---

## Error Handling

| Error | Action |
|-------|--------|
| Token expired | Auto-refresh via `google-auth`; if fails → log + alert |
| Rate limit (429) | Exponential backoff: 2s → 4s → 8s → 16s → stop |
| Network timeout | Retry 3 times, then wait full interval |
| Vault path missing | Log error + exit with code 1 |
| `credentials.json` missing | Print setup instructions + exit |

---

## Reference Files

| File | When to Read |
|------|--------------|
| `references/gmail-api-reference.md` | Gmail API query syntax, label IDs |
| `references/oauth-setup-guide.md` | Step-by-step OAuth credentials setup |
| `references/process-management.md` | PM2, supervisord, systemd options |
| `scripts/gmail_watcher.py` | Main watcher implementation |
