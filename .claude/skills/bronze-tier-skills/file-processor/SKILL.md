---
name: file-processor
description: |
  Reads action files from an Obsidian vault's /Needs_Action folder, reasons about
  each item using Company_Handbook.md rules, creates structured Plan.md files,
  routes items requiring approval to /Pending_Approval, and moves completed items
  to /Done. Implements the core Claude Code read-think-plan-write loop.
  This skill should be used when users want Claude to process inbox items, triage
  messages, create action plans, or run the core AI Employee reasoning cycle.
allowed-tools: Read, Write, Glob, Bash
---

# File Processor

Claude's core reasoning loop: read vault items, reason, plan, route, and archive.

## What This Skill Does

- Reads all `.md` files from `/Needs_Action`
- Loads `Company_Handbook.md` for rules and autonomy thresholds
- Creates `PLAN_*.md` files in `/Plans` for each item
- Routes sensitive actions to `/Pending_Approval`
- Moves processed items to `/Done`
- Updates `Dashboard.md` with activity summary

## What This Skill Does NOT Do

- Send emails or messages (requires MCP at Silver tier)
- Execute payments (always requires human approval)
- Process items in `/Pending_Approval` (those wait for human)
- Continuously monitor — run on-demand or via orchestrator trigger

---

## Before Implementation

Gather context before processing:

| Source | Gather |
|--------|--------|
| **Codebase** | List files in `/Needs_Action`, read `Company_Handbook.md` |
| **Conversation** | Any specific items or priorities the user wants addressed first |
| **Skill References** | Routing rules from `references/routing-rules.md` |
| **User Guidelines** | Any overrides to handbook rules for this session |

Read `Company_Handbook.md` FIRST — it defines what is auto-approved vs. what requires human review.

---

## Processing Workflow

```
Read Company_Handbook.md
        ↓
List all files in /Needs_Action
        ↓
For each file:
    ├── Parse frontmatter + content
    ├── Apply handbook routing rules
    ├── Create PLAN_*.md in /Plans
    ├── Route to /Pending_Approval (if approval needed)
    └── Move source file to /Done
        ↓
Update Dashboard.md
```

### Step 1 – Load Rules

Read `Company_Handbook.md`. Extract:
- Autonomy thresholds table
- Priority keywords
- Communication rules
- Financial limits

### Step 2 – List Items

```bash
ls {vault_path}/Needs_Action/*.md
```

If empty → log "No items to process" and exit cleanly.

### Step 3 – Process Each Item

For each file, apply the decision tree in `references/routing-rules.md`:

| Item Type | Condition | Route to |
|-----------|-----------|----------|
| Email | Known contact, low value | Create plan + `/Done` |
| Email | New contact OR high value | `/Pending_Approval` |
| WhatsApp | Contains priority keyword | `/Pending_Approval` |
| WhatsApp | Routine message | Create plan + `/Done` |
| File drop | Any | Create plan, review with user |
| Payment | Any amount | Always `/Pending_Approval` |

### Step 4 – Create Plan File

Write `PLAN_<slug>.md` to `/Plans` for every processed item.
Use the template in `assets/plan-template.md`.

### Step 5 – Create Approval Request (if needed)

Write `APPROVAL_<action>_<date>.md` to `/Pending_Approval`.
Use the template in `assets/approval-template.md`.
Set `expires` to 24 hours from now.

### Step 6 – Archive Source

Move processed source file from `/Needs_Action` → `/Done`.

```python
shutil.move(str(source_file), str(done_dir / source_file.name))
```

### Step 7 – Update Dashboard

Append to the `## Recent Activity` section of `Dashboard.md`.
Update the `Pending actions` count.

---

## Plan File Schema

```yaml
---
type: plan
source_file: EMAIL_18f3a2b.md
created: 2026-01-07T10:30:00Z
status: pending | pending_approval | done
requires_approval: true | false
---

## Objective
<What needs to happen>

## Steps
- [x] Step already reasoned about
- [ ] Step requiring action

## Approval Required
<Describe what approval is needed, if any>
```

---

## Error Handling

| Error | Action |
|-------|--------|
| Malformed frontmatter | Log warning, move to `/Done` with `status: parse_error` |
| `Company_Handbook.md` missing | Halt processing, alert user to run vault-setup |
| Cannot move file | Log error, leave in `/Needs_Action`, retry next cycle |
| Unknown item type | Default to requiring approval (safe fallback) |

---

## Anti-Patterns to Avoid

- Never delete source files — always move to `/Done`
- Never auto-approve payments or new-contact emails
- Never process items in `/Pending_Approval` — those belong to the human
- Never overwrite an existing `PLAN_*.md` — append `_v2` suffix

---

## Reference Files

| File | When to Read |
|------|--------------|
| `references/routing-rules.md` | Decision tree for routing action items |
| `references/frontmatter-parsing.md` | How to parse YAML frontmatter in Python |
| `assets/plan-template.md` | Template for PLAN_*.md files |
| `assets/approval-template.md` | Template for APPROVAL_*.md files |
| `scripts/process_files.py` | Automated file processing script |
