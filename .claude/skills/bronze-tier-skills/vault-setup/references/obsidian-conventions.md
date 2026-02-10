# Obsidian Conventions for AI Employee Vault

## Frontmatter Schema

Every action file written by a Watcher or Claude must include YAML frontmatter:

```yaml
---
type: email | whatsapp | file_drop | plan | approval_request | briefing
status: pending | in_progress | approved | rejected | done
created: ISO-8601 timestamp
priority: high | medium | low          # optional
agent: claude-local | claude-cloud     # optional, for multi-agent tiers
---
```

## File Naming Conventions

| Content | Pattern | Example |
|---------|---------|---------|
| Email action | `EMAIL_<message_id>.md` | `EMAIL_18f3a2b.md` |
| WhatsApp action | `WHATSAPP_<contact>_<date>.md` | `WHATSAPP_client_a_2026-01-07.md` |
| File drop | `FILE_<original_name>.md` | `FILE_invoice.pdf.md` |
| Plan | `PLAN_<task_slug>.md` | `PLAN_invoice_client_a.md` |
| Approval | `APPROVAL_<action>_<date>.md` | `APPROVAL_payment_2026-01-07.md` |
| Briefing | `YYYY-MM-DD_Monday_Briefing.md` | `2026-01-06_Monday_Briefing.md` |
| Log | `YYYY-MM-DD.json` | `2026-01-07.json` |

## Markdown Rules

- Use `- [ ]` checkboxes for action items Claude should track
- Use `## Suggested Actions` section in every Watcher-generated file
- Use `[[WikiLinks]]` to link related notes (Obsidian Graph view)
- Use `#tags` for filtering: `#urgent`, `#invoice`, `#payment`, `#social`
- Keep files under 50KB for Obsidian performance

## Dashboard Update Pattern

Dashboard.md is the SINGLE SOURCE OF TRUTH for current state.
Only one agent writes to it at a time (single-writer rule).
Structure:

```markdown
## Status
- Last updated: {{timestamp}}
- Pending actions: {{count}}
- This week revenue: ${{amount}}

## Recent Activity
- [{{timestamp}}] {{action_description}}

## Alerts
- {{any high-priority items}}
```
