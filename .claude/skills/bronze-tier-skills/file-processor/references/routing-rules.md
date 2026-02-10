# Routing Rules

Decision tree Claude applies to each item in `/Needs_Action`.

## Rule Priority Order

1. Safety rules (always checked first)
2. Financial rules
3. Communication rules
4. Default fallback

---

## Safety Rules (Always Apply)

| Condition | Route |
|-----------|-------|
| `type: payment` | → `/Pending_Approval` always, no exceptions |
| Any delete/move outside vault | → `/Pending_Approval` |
| Sender is new (first time seen) | → `/Pending_Approval` |
| Amount > $100 | → `/Pending_Approval` |

---

## Email Routing

```
Is sender in known contacts?
├── YES → Is subject/body high-priority keyword?
│         ├── YES → Create plan + route to /Pending_Approval (draft reply)
│         └── NO  → Create plan + move to /Done (for later)
└── NO  → Always route to /Pending_Approval
```

---

## WhatsApp Routing

```
Does message contain priority keyword?
├── YES → Create plan + route to /Pending_Approval
└── NO  → Create plan + move to /Done (log for weekly review)
```

Priority keywords (from Company_Handbook.md):
urgent, asap, invoice, payment, complaint, cancel, refund, emergency

---

## File Drop Routing

```
What is the file type?
├── .pdf / .docx → Create plan noting "document received, review needed"
│                  Route to /Pending_Approval
├── .csv / .xlsx → Create plan noting "data file received"
│                  Move to /Accounting/ if financial; else /Done
└── other        → Create plan + move to /Done
```

---

## Default Fallback

**When in doubt → route to `/Pending_Approval`.**

Never auto-approve something Claude isn't confident about.
Write a plan explaining WHY the item needs human review.

---

## Status Codes

Use these `status` values consistently:

| Status | Meaning |
|--------|---------|
| `pending` | Not yet processed |
| `in_progress` | Claude is working on it |
| `pending_approval` | Waiting for human |
| `approved` | Human approved, ready to act |
| `rejected` | Human rejected |
| `done` | Completed and archived |
| `parse_error` | Malformed file, needs review |
