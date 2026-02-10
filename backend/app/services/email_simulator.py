import random
import uuid
from datetime import datetime, timezone, timedelta

from app.config import settings


# ---------------------------------------------------------------------------
# Email template pool (at least 8 varieties)
# ---------------------------------------------------------------------------

EMAIL_TEMPLATES = [
    {
        "sender": "accounts@vendorsupply.com",
        "subject": "Invoice #{inv_num} - Amount Due ${amount}",
        "body": "Please find attached invoice #{inv_num} for ${amount}. Payment is due within 30 days. If you have any questions regarding this invoice, please contact our billing department.",
        "type": "payment",
        "priority": "normal",
        "vars": {"inv_num": lambda: str(random.randint(10000, 99999)), "amount": lambda: f"{random.randint(50, 5000):.2f}"},
    },
    {
        "sender": "angry.customer@email.com",
        "subject": "Complaint: Terrible service experience",
        "body": "I am extremely unhappy with the service I received. My order was delayed by two weeks and nobody responded to my emails. I want a full refund or I will escalate this further. This is unacceptable.",
        "type": "email",
        "priority": "high",
        "vars": {},
    },
    {
        "sender": "john.smith@partnercorp.com",
        "subject": "Meeting Request: Q{quarter} Partnership Review",
        "body": "Hi, I would like to schedule a meeting to discuss our partnership progress for Q{quarter}. Could we find a time next week? I have availability on Tuesday and Thursday afternoons.",
        "type": "email",
        "priority": "normal",
        "vars": {"quarter": lambda: str(random.randint(1, 4))},
    },
    {
        "sender": "payments@stripe.com",
        "subject": "Payment Confirmation - ${amount} received",
        "body": "We have successfully processed a payment of ${amount} from client #{client_id}. The funds will be available in your account within 2 business days. Transaction reference: TXN-{txn_ref}.",
        "type": "payment",
        "priority": "normal",
        "vars": {
            "amount": lambda: f"{random.randint(100, 10000):.2f}",
            "client_id": lambda: str(random.randint(1000, 9999)),
            "txn_ref": lambda: uuid.uuid4().hex[:8].upper(),
        },
    },
    {
        "sender": "dev.team@clientapp.io",
        "subject": "URGENT: Critical bug in production system",
        "body": "We have discovered a critical bug in the production deployment that is affecting all users. The checkout flow is broken and customers cannot complete purchases. This needs immediate attention. Emergency fix required ASAP.",
        "type": "email",
        "priority": "high",
        "vars": {},
    },
    {
        "sender": "sarah.jones@newclient.com",
        "subject": "New Business Inquiry - {service} Services",
        "body": "Hello, I found your company through a referral and I am interested in learning more about your {service} services. We are a mid-size company looking for a reliable partner. Could you send me your pricing and availability?",
        "type": "email",
        "priority": "normal",
        "vars": {"service": lambda: random.choice(["consulting", "development", "marketing", "design", "analytics"])},
    },
    {
        "sender": "billing@saasplatform.com",
        "subject": "Subscription Renewal Notice - Plan expires in {days} days",
        "body": "Your subscription to the Professional plan is set to expire in {days} days. To avoid any interruption in service, please renew your subscription. Your current rate is ${amount}/month. Renew now to lock in this price.",
        "type": "email",
        "priority": "normal",
        "vars": {
            "days": lambda: str(random.randint(3, 14)),
            "amount": lambda: f"{random.choice([29, 49, 99, 149, 199]):.2f}",
        },
    },
    {
        "sender": "mike.wilson@company.com",
        "subject": "Expense Report - {month} {year}",
        "body": "Please review and approve my expense report for {month} {year}. Total amount: ${amount}. Expenses include travel, client meals, and office supplies. Receipts are attached. Please process payment at your earliest convenience.",
        "type": "payment",
        "priority": "normal",
        "vars": {
            "month": lambda: random.choice(["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]),
            "year": lambda: "2026",
            "amount": lambda: f"{random.randint(200, 3000):.2f}",
        },
    },
    {
        "sender": "noreply@overdue-collections.com",
        "subject": "OVERDUE: Invoice #{inv_num} - Payment Required Immediately",
        "body": "This is a final reminder that invoice #{inv_num} for ${amount} is now {days} days overdue. Immediate payment is required to avoid late fees and potential service suspension. Please remit payment ASAP.",
        "type": "payment",
        "priority": "high",
        "vars": {
            "inv_num": lambda: str(random.randint(10000, 99999)),
            "amount": lambda: f"{random.randint(500, 8000):.2f}",
            "days": lambda: str(random.randint(15, 60)),
        },
    },
    {
        "sender": "legal@partnerfirm.com",
        "subject": "Contract Amendment - Review Required",
        "body": "Attached please find the proposed amendment to our service agreement. Key changes include updated payment terms, revised SLA targets, and new data handling provisions. Please review and provide feedback within 5 business days.",
        "type": "email",
        "priority": "normal",
        "vars": {},
    },
]


def _render_template(template: dict) -> dict:
    """Resolve template variables and return a concrete email dict."""
    # Generate variable values
    var_values: dict[str, str] = {}
    for key, generator in template["vars"].items():
        var_values[key] = generator()

    # Render subject and body
    subject = template["subject"]
    body = template["body"]
    for key, val in var_values.items():
        subject = subject.replace("{" + key + "}", val)
        body = body.replace("{" + key + "}", val)

    return {
        "sender": template["sender"],
        "subject": subject,
        "body": body,
        "type": template["type"],
        "priority": template["priority"],
    }


def simulate_email(
    sender: str,
    subject: str,
    body: str,
    email_type: str = "email",
    priority: str = "normal",
) -> tuple[str, str]:
    """
    Write an EMAIL_*.md file to Needs_Action/ with proper frontmatter.
    Returns (message, filename).
    """
    vault = settings.vault_dir
    needs_action_dir = vault / "Needs_Action"
    needs_action_dir.mkdir(parents=True, exist_ok=True)

    email_id = uuid.uuid4().hex[:8]
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    filename = f"EMAIL_{email_id}.md"
    filepath = needs_action_dir / filename

    content = f"""\
---
type: {email_type}
id: {email_id}
from: {sender}
subject: {subject}
received: {timestamp}
priority: {priority}
status: needs_action
---

# {subject}

**From**: {sender}
**Date**: {timestamp}
**Priority**: {priority}

---

{body}
"""
    filepath.write_text(content, encoding="utf-8")
    return f"Email simulated: {filename}", filename


def simulate_batch(count: int = 5) -> tuple[str, int, list[str]]:
    """
    Generate a batch of random realistic emails.
    Returns (message, count, filenames).
    """
    filenames: list[str] = []

    # Pick random templates (with possible repeats if count > len(templates))
    chosen = random.choices(EMAIL_TEMPLATES, k=count)

    for template in chosen:
        rendered = _render_template(template)
        _, filename = simulate_email(
            sender=rendered["sender"],
            subject=rendered["subject"],
            body=rendered["body"],
            email_type=rendered["type"],
            priority=rendered["priority"],
        )
        filenames.append(filename)

    message = f"Generated {count} simulated emails in Needs_Action/"
    return message, count, filenames
