# Rule Templates by Business Type

## Template: Freelancer / Consultant

Suitable for solo practitioners, consultants, coaches.

### Autonomy Thresholds
| Action | Auto-Approve | Requires Approval |
|--------|-------------|-------------------|
| Read emails | ✅ Always | — |
| Draft email reply | ✅ Known contacts | New contacts, bulk |
| Send email | ❌ Never | Always |
| Create plan file | ✅ Always | — |
| Log transaction | ✅ Always | — |
| Make payment | ❌ Never | Always |
| Social media draft | ✅ Create draft | Publish |
| Delete files | ❌ Never | Always |

### Financial Rules
- Flag any payment over **$100**
- ALL new payees require approval regardless of amount
- Flag recurring charges over $50/month
- Flag any charge increase > 10%

### Priority Keywords
urgent, asap, contract, proposal, invoice, payment, overdue, refund,
complaint, testimonial, referral, scope creep, revision

---

## Template: Agency / Team

Suitable for small agencies, studios, teams.

### Autonomy Thresholds
| Action | Auto-Approve | Requires Approval |
|--------|-------------|-------------------|
| Read emails | ✅ Always | — |
| Draft client email | ✅ Existing clients | New clients |
| Send email | ❌ Never | Owner always approves |
| Forward internally | ✅ Team members | External |
| Create plan file | ✅ Always | — |
| Log transaction | ✅ Always | — |
| Client payment | ❌ Never | Always |
| Vendor payment | ❌ Never | Always |
| Social post draft | ✅ Prepared drafts | Anything off-schedule |

### Financial Rules
- Flag any payment over **$200**
- ALL new payees require approval
- Monthly vendor reviews for subscriptions > $100
- Flag scope change requests in emails for project management

### Priority Keywords
urgent, asap, deadline, scope change, budget, invoice, contract, approval,
escalate, complaint, legal, NDA, revision, feedback, bug, outage

---

## Template: E-commerce

Suitable for online stores, product businesses.

### Autonomy Thresholds
| Action | Auto-Approve | Requires Approval |
|--------|-------------|-------------------|
| Log order | ✅ Always | — |
| Draft order confirmation | ✅ Always | — |
| Send order confirmation | ✅ Automated only | Manual sends |
| Process refund < $50 | ✅ Policy-compliant | > $50 always |
| Process refund > $50 | ❌ Never | Always |
| Social post | ❌ Never | Always |
| Price change | ❌ Never | Always |

### Financial Rules
- Auto-approve refunds **under $50** for known customers (policy-based)
- Flag refunds **over $50** always
- Flag chargeback notices immediately as `priority: high`
- Flag payment processor fee increases > 5%

### Priority Keywords
chargeback, dispute, refund, return, damaged, missing order, wrong item,
cancel, complaint, legal, fraud, out of stock, reorder

---

## Template: General / Default

Safe defaults for any business type.

### Autonomy Thresholds
| Action | Auto-Approve | Requires Approval |
|--------|-------------|-------------------|
| Read/log emails | ✅ Always | — |
| Draft replies | ✅ Known contacts | New contacts |
| Send anything | ❌ Never | Always |
| Create files | ✅ Always | — |
| Log data | ✅ Always | — |
| Payments | ❌ Never | Always |
| Deletions | ❌ Never | Always |

### Financial Rules
- Flag any payment over **$100**
- ALL new payees require approval
- Flag any amount increase on recurring charges

### Priority Keywords
urgent, asap, invoice, payment, complaint, cancel, legal, refund, emergency
