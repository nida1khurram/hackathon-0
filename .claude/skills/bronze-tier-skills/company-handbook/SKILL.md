---
name: company-handbook
description: |
  Creates, validates, and applies a Company_Handbook.md — the Rules of Engagement
  file that governs how the AI Employee behaves. Encodes autonomy thresholds,
  communication rules, financial limits, priority keywords, and escalation paths.
  This skill should be used when users want to create their first handbook, update
  autonomy rules, add new communication guidelines, define financial limits, or
  troubleshoot Claude acting incorrectly due to missing or vague handbook rules.
allowed-tools: Read, Write, Glob
---

# Company Handbook

Create and maintain the Rules of Engagement that govern AI Employee behavior.

## What This Skill Does

- Creates a well-structured `Company_Handbook.md` tailored to the user's business
- Validates existing handbook for missing critical sections
- Guides users in setting appropriate autonomy thresholds
- Provides rule templates for common business types (freelancer, agency, e-commerce)
- Explains how Claude reads and applies handbook rules during processing

## What This Skill Does NOT Do

- Enforce rules automatically at runtime (file-processor skill does that)
- Store credentials or sensitive data (those go in `.env`)
- Replace legal documents or employment contracts
- Handle compliance-specific rules (GDPR, HIPAA) without user input

---

## Before Implementation

Gather context before creating the handbook:

| Source | Gather |
|--------|--------|
| **Conversation** | Business type, owner name, communication preferences, financial limits |
| **Codebase** | Existing `Company_Handbook.md` to avoid overwriting if already set up |
| **Skill References** | Rule templates from `references/rule-templates.md` |

Key questions to ask (only these — don't ask for domain knowledge):
1. What type of business? (freelancer / agency / e-commerce / other)
2. What's your payment approval threshold? (default: $100)
3. Any custom priority keywords for YOUR industry?

---

## Handbook Creation Workflow

```
Ask 3 questions (business type, threshold, keywords)
        ↓
Select matching rule template
        ↓
Customize with user's answers
        ↓
Write Company_Handbook.md
        ↓
Validate completeness
        ↓
Explain key rules to user
```

### Step 1 – Gather Requirements

Minimum required from user:
- Business name and owner name (from vault-setup if already run)
- Business type (to select template)
- Payment approval threshold

### Step 2 – Select Template

| Business Type | Template |
|---------------|----------|
| Freelancer / Consultant | Solo-focused, all payments need approval, tight email rules |
| Agency / Team | Team communication rules, delegated approvals |
| E-commerce | Order fulfillment rules, refund thresholds, customer service tone |
| General / Other | Balanced defaults |

See full templates in `references/rule-templates.md`.

### Step 3 – Write Handbook

Write to `{vault_path}/Company_Handbook.md`.
Check if file exists → ask before overwriting.
Substitute user's answers into the appropriate template.

### Step 4 – Validate Handbook

After writing, verify all required sections are present:

```
Required sections checklist:
- [ ] ## 1. Identity (owner, business, AI name)
- [ ] ## 2. Communication Rules (email + WhatsApp)
- [ ] ## 3. Financial Rules (payment thresholds)
- [ ] ## 4. Autonomy Thresholds (table)
- [ ] ## 5. Priority Keywords (list)
- [ ] ## 6. Business Hours
- [ ] ## 7. Privacy Rules
- [ ] ## 8. Escalation Path
```

If any section is missing → add it with safe defaults.

---

## How Claude Applies Handbook Rules

At runtime, the file-processor skill:

1. Reads `Company_Handbook.md` before processing any item
2. Extracts the Autonomy Thresholds table → decides auto vs approval
3. Extracts Priority Keywords → sets `priority: high` on matched items
4. Extracts Financial Rules → routes any payment item to `/Pending_Approval`
5. Extracts Communication Rules → guides plan file content

**The handbook is the source of truth.** If Claude behaves incorrectly, update the handbook — not the code.

---

## Updating the Handbook

To change a rule, instruct Claude naturally:
- "Add 'contract' to the priority keywords"
- "Change the payment threshold to $200"
- "Allow Claude to draft LinkedIn posts without approval"

Claude will:
1. Read the current handbook
2. Find the relevant section
3. Make the specific change
4. Confirm what was changed

---

## Error Handling

| Error | Action |
|-------|--------|
| Handbook missing at runtime | file-processor halts and alerts user |
| Missing required section | Auto-add with safe (conservative) defaults |
| Conflicting rules | Flag to user and ask for clarification |
| File permission denied | Report error with path and permissions needed |

---

## Anti-Patterns to Avoid

- Never put API keys or passwords in the handbook (use `.env`)
- Never set ALL actions to auto-approve — always keep payments as approval-required
- Never delete sections — if you want to disable a rule, comment it out with `<!--`
- Never use vague language like "important emails" — use specific keywords

---

## Reference Files

| File | When to Read |
|------|--------------|
| `references/rule-templates.md` | Complete handbook templates by business type |
| `references/autonomy-guide.md` | Guide for setting appropriate autonomy levels |
| `references/handbook-validator.md` | Validation checklist and common mistakes |
| `scripts/validate_handbook.py` | Script to check handbook completeness |
