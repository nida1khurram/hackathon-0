---
name: vault-setup
description: |
  Scaffolds and initializes an Obsidian vault for use as a Personal AI Employee
  dashboard. Creates the required folder structure, core markdown files, and
  configuration needed for a Digital FTE system.
  This skill should be used when users want to set up their AI Employee vault
  from scratch, reset the vault structure, or add missing scaffold components
  (Dashboard.md, Company_Handbook.md, folder hierarchy).
allowed-tools: Read, Write, Glob, Bash
---

# Vault Setup

Initialize a production-ready Obsidian vault for a Personal AI Employee.

## What This Skill Does

- Creates the standard folder hierarchy (`/Inbox`, `/Needs_Action`, `/Done`, `/Plans`, `/Logs`, `/Pending_Approval`, `/Approved`, `/Rejected`, `/Briefings`, `/Accounting`)
- Generates `Dashboard.md` with live-summary schema
- Generates `Company_Handbook.md` with Rules of Engagement template
- Generates `Business_Goals.md` with KPI schema
- Writes `.gitignore` to protect secrets

## What This Skill Does NOT Do

- Install Obsidian or plugins
- Configure Claude Code MCP servers
- Migrate existing vault data
- Set up Git sync or Syncthing

---

## Before Implementation

Gather context before scaffolding:

| Source | Gather |
|--------|--------|
| **Conversation** | Vault root path, business name, owner name |
| **Codebase** | Existing vault files to avoid overwriting |
| **User Guidelines** | Any custom folders or rules the user already has |

Ask only: (1) vault path, (2) your name / business name. Everything else is embedded below.

---

## Workflow

```
Ask vault path + owner name
        ↓
Check for existing files (avoid overwrite)
        ↓
Create folder hierarchy
        ↓
Write core markdown files from assets/
        ↓
Write .gitignore
        ↓
Confirm structure to user
```

### Step 1 – Resolve Vault Path

Use the path the user provides. Default: `~/AI_Employee_Vault`.

### Step 2 – Safety Check

Before writing, run:
```bash
ls {vault_path}
```
If `Dashboard.md` already exists → ask before overwriting.

### Step 3 – Create Folders

Create all folders listed in `references/folder-schema.md`.
Use `mkdir -p` (idempotent — safe to run on existing vault).

```bash
mkdir -p {vault_path}/{Inbox,Needs_Action,Done,Plans,Logs,Pending_Approval,Approved,Rejected,Briefings,Accounting,In_Progress}
```

### Step 4 – Write Core Files

Use templates from `assets/`. Substitute `{{OWNER}}` and `{{BUSINESS}}` tokens.

| File | Template |
|------|----------|
| `Dashboard.md` | `assets/dashboard-template.md` |
| `Company_Handbook.md` | `assets/handbook-template.md` |
| `Business_Goals.md` | `assets/goals-template.md` |
| `.gitignore` | `assets/gitignore-template.txt` |

### Step 5 – Confirm

Print the final tree to user:
```bash
find {vault_path} -maxdepth 2 | sort
```

---

## Error Handling

| Error | Action |
|-------|--------|
| Permission denied | Tell user to check folder permissions |
| Path not found | Offer to create parent directories |
| File already exists | Ask before overwriting — never silently replace |
| Disk full | Alert immediately, do not partial-write |

---

## Anti-Patterns to Avoid

- Never store API keys or tokens inside the vault
- Never create `.env` inside the vault root (put it in project root, add to `.gitignore`)
- Never name files with spaces (use underscores for Obsidian compatibility)
- Never skip the `.gitignore` — credentials must be excluded from version control

---

## Reference Files

| File | When to Read |
|------|--------------|
| `references/folder-schema.md` | Complete folder list with purpose of each |
| `references/obsidian-conventions.md` | Markdown frontmatter, linking, tagging conventions |
| `assets/dashboard-template.md` | Dashboard.md starter template |
| `assets/handbook-template.md` | Company_Handbook.md starter template |
| `assets/goals-template.md` | Business_Goals.md starter template |
| `assets/gitignore-template.txt` | Safe .gitignore for AI Employee vaults |
| `scripts/init_vault.py` | Automated scaffolding script |
