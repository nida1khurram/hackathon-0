from pathlib import Path
from datetime import datetime, timezone

from app.config import settings
from app.models.vault import VaultStatus, FolderStatus, CoreFileStatus


FOLDERS = [
    "Inbox",
    "Needs_Action",
    "In_Progress",
    "Plans",
    "Pending_Approval",
    "Approved",
    "Rejected",
    "Done",
    "Logs",
    "Briefings",
    "Accounting",
]

CORE_FILES = [
    "Dashboard.md",
    "Company_Handbook.md",
    "Business_Goals.md",
    ".gitignore",
]

# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

DASHBOARD_TEMPLATE = """\
---
type: dashboard
last_updated: {{TIMESTAMP}}
---

# AI Employee Dashboard - {{BUSINESS}}

## Status

| Metric | Value |
|--------|-------|
| Last updated | {{TIMESTAMP}} |
| Pending actions | 0 |
| Awaiting approval | 0 |
| Completed today | 0 |
| MTD Revenue | $0.00 |
| Agent health | Online |

## Alerts

No alerts. All clear.

## Recent Activity

No activity yet.
"""

HANDBOOK_TEMPLATE = """\
---
type: handbook
owner: {{OWNER}}
business: {{BUSINESS}}
last_updated: {{TIMESTAMP}}
---

# Company Handbook - {{BUSINESS}}

This handbook defines how the AI Employee operates on behalf of {{OWNER}}.

---

## 1. Identity

- **Owner**: {{OWNER}}
- **Business**: {{BUSINESS}}
- **AI Employee Name**: AI Assistant
- **Role**: Autonomous business operations assistant
- **Created**: {{TIMESTAMP}}

---

## 2. Communication Rules

- Always reply professionally and courteously.
- Use the business name in email signatures.
- Do not share internal data with external contacts.
- Email responses should be concise and action-oriented.
- WhatsApp messages should be brief and informal but professional.
- Never send messages outside business hours unless marked urgent.

---

## 3. Financial Rules

- **Auto-approve threshold**: $100.00
- **Requires owner approval**: Any amount above $100.00
- **Payment methods**: As configured by owner
- Invoices above threshold must be routed to Pending_Approval.
- Always log financial transactions in the Accounting folder.
- Never authorize refunds above $50.00 without approval.

---

## 4. Autonomy Thresholds

| Action | Auto-Approve | Requires Approval |
|--------|-------------|-------------------|
| Reply to email | Yes | No |
| Schedule meeting | Yes | No |
| Send payment < $100 | Yes | No |
| Send payment >= $100 | No | Yes |
| Issue refund < $50 | Yes | No |
| Issue refund >= $50 | No | Yes |
| Delete files | No | Yes |
| Change handbook | No | Yes |
| New vendor setup | No | Yes |

---

## 5. Priority Keywords

The following keywords trigger high-priority routing:

- **Urgent**: urgent, asap, immediately, emergency
- **Financial**: invoice, payment, overdue, refund
- **Complaint**: complaint, unhappy, cancel, disappointed
- **Legal**: legal, lawsuit, compliance, regulation

---

## 6. Business Hours

- **Monday - Friday**: 9:00 AM - 6:00 PM
- **Saturday**: 10:00 AM - 2:00 PM
- **Sunday**: Closed
- **Timezone**: Local timezone of owner
- **After-hours behavior**: Queue non-urgent items, escalate urgent items immediately.

---

## 7. Privacy Rules

- Never share customer personal data externally.
- Redact sensitive information (SSN, credit cards) from logs.
- Do not store passwords in plain text.
- All data stays within the vault unless explicitly authorized.
- Comply with applicable data protection regulations.

---

## 8. Escalation Path

When uncertain or when an error occurs:

1. **Check handbook** for relevant rules.
2. **Log the issue** in the Logs folder with full details.
3. **Create approval request** if action requires owner sign-off.
4. **Notify owner** via preferred communication channel.
5. **Do not proceed** with the action until approved.
6. **If critical**: Mark as urgent and escalate immediately.
"""

GOALS_TEMPLATE = """\
---
type: goals
owner: {{OWNER}}
business: {{BUSINESS}}
last_updated: {{TIMESTAMP}}
---

# Business Goals - {{BUSINESS}}

## Revenue Targets

| Period | Target | Actual | Status |
|--------|--------|--------|--------|
| This Month | $5,000.00 | $0.00 | In Progress |
| This Quarter | $15,000.00 | $0.00 | In Progress |
| This Year | $60,000.00 | $0.00 | In Progress |

## Active Goals

1. **Set up AI employee operations** - Configure all vault folders, handbook, and automation rules.
2. **Process first batch of emails** - Demonstrate email processing and routing capabilities.
3. **Establish approval workflow** - Ensure all high-value actions go through owner approval.

## Key Metrics

- Customer satisfaction: N/A
- Response time: N/A
- Tasks completed: 0
- Revenue processed: $0.00

## Notes

Initial setup. Update this file as business goals evolve.
"""

GITIGNORE_TEMPLATE = """\
# OS files
.DS_Store
Thumbs.db

# Editor files
*.swp
*.swo
*~

# Sensitive data
*.env
credentials.*
secrets.*

# Temporary files
*.tmp
*.bak
"""


def _render(template: str, owner: str, business: str) -> str:
    """Replace template placeholders with actual values."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    return (
        template.replace("{{OWNER}}", owner)
        .replace("{{BUSINESS}}", business)
        .replace("{{TIMESTAMP}}", timestamp)
    )


def get_vault_status() -> VaultStatus:
    """Check the current state of the vault directory."""
    vault = settings.vault_dir
    initialized = vault.exists()

    folders: list[FolderStatus] = []
    for folder_name in FOLDERS:
        folder_path = vault / folder_name
        if folder_path.exists():
            count = len(list(folder_path.glob("*.md")))
        else:
            count = 0
        folders.append(FolderStatus(name=folder_name, count=count))

    core_files: list[CoreFileStatus] = []
    for fname in CORE_FILES:
        core_files.append(CoreFileStatus(name=fname, exists=(vault / fname).exists()))

    return VaultStatus(
        initialized=initialized,
        folders=folders,
        core_files=core_files,
    )


def init_vault(owner: str, business: str) -> str:
    """Create all vault folders and write template core files."""
    vault = settings.vault_dir

    # Create all folders
    for folder_name in FOLDERS:
        (vault / folder_name).mkdir(parents=True, exist_ok=True)

    # Write core files
    templates = {
        "Dashboard.md": DASHBOARD_TEMPLATE,
        "Company_Handbook.md": HANDBOOK_TEMPLATE,
        "Business_Goals.md": GOALS_TEMPLATE,
        ".gitignore": GITIGNORE_TEMPLATE,
    }

    for filename, template in templates.items():
        filepath = vault / filename
        content = _render(template, owner, business)
        filepath.write_text(content, encoding="utf-8")

    return f"Vault initialized at {vault} with {len(FOLDERS)} folders and {len(templates)} core files."
