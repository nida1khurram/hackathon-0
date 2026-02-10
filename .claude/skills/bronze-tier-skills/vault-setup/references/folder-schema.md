# Folder Schema

All folders created by the vault-setup skill.

| Folder | Purpose |
|--------|---------|
| `/Inbox` | Raw drops from watchers before triage |
| `/Needs_Action` | Triaged items requiring Claude processing |
| `/In_Progress` | Items claimed by an agent (claim-by-move rule) |
| `/Plans` | Plan.md files created by Claude during reasoning |
| `/Pending_Approval` | Actions awaiting human approval |
| `/Approved` | Human-approved actions ready to execute |
| `/Rejected` | Human-rejected actions for audit |
| `/Done` | Completed tasks (archive) |
| `/Logs` | JSON audit logs (YYYY-MM-DD.json) |
| `/Briefings` | Monday Morning CEO Briefings |
| `/Accounting` | Bank transactions, invoices, rates |

## Claim-by-Move Rule

When multiple agents are running (Silver/Gold tiers), the first agent to move an item
from `/Needs_Action` → `/In_Progress/<agent_name>/` owns it.
All other agents must skip it.
At Bronze tier (single agent), this folder is reserved for future use.

## Security Rule

Never sync secrets. The following must NEVER appear in the vault:
- `.env` files
- OAuth tokens / `credentials.json`
- WhatsApp session folders
- Banking API keys
