import pytest


def _simulate_normal_email(client):
    """Helper: create a normal email that does NOT need approval."""
    resp = client.post("/api/simulate/email", json={
        "sender": "friend@example.com",
        "subject": "Lunch tomorrow",
        "body": "Want to grab lunch tomorrow at noon?",
        "type": "email",
        "priority": "normal",
    })
    return resp.json()["filename"]


def _simulate_urgent_email(client):
    """Helper: create an email that triggers approval (priority keyword)."""
    resp = client.post("/api/simulate/email", json={
        "sender": "boss@example.com",
        "subject": "URGENT: Server is down",
        "body": "The production server is down. Fix immediately!",
        "type": "email",
        "priority": "high",
    })
    return resp.json()["filename"]


def _simulate_payment(client):
    """Helper: create a payment-type item that always needs approval."""
    resp = client.post("/api/simulate/email", json={
        "sender": "vendor@example.com",
        "subject": "Invoice #1234",
        "body": "Please pay invoice #1234 for $500.",
        "type": "payment",
        "priority": "normal",
    })
    return resp.json()["filename"]


# ── Tests ─────────────────────────────────────────────────────────────────

def test_list_empty(client, initialized_vault):
    """Empty Needs_Action folder returns an empty list."""
    resp = client.get("/api/needs-action")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_after_simulate(client, initialized_vault):
    """Items appear in the list after simulating emails."""
    _simulate_normal_email(client)
    _simulate_urgent_email(client)
    resp = client.get("/api/needs-action")
    items = resp.json()
    assert len(items) == 2


def test_process_single(client, initialized_vault):
    """Processing a single item returns a success action string."""
    filename = _simulate_normal_email(client)
    resp = client.post("/api/needs-action/process", json={"filename": filename})
    assert resp.status_code == 200
    assert "action" in resp.json()


def test_process_not_found(client, initialized_vault):
    """Processing a non-existent file returns 404."""
    resp = client.post(
        "/api/needs-action/process",
        json={"filename": "DOES_NOT_EXIST.md"},
    )
    assert resp.status_code == 404


def test_process_all(client, initialized_vault):
    """Process-all returns correct count and clears Needs_Action."""
    _simulate_normal_email(client)
    _simulate_normal_email(client)
    resp = client.post("/api/needs-action/process-all")
    assert resp.status_code == 200
    data = resp.json()
    assert data["processed"] == 2
    assert len(data["actions"]) == 2
    # Needs_Action should be empty now
    assert client.get("/api/needs-action").json() == []


def test_process_routes_to_done(client, initialized_vault, vault_dir):
    """A normal email (no priority keywords) is moved to Done."""
    filename = _simulate_normal_email(client)
    client.post("/api/needs-action/process", json={"filename": filename})
    assert (vault_dir / "Done" / filename).exists()
    assert not (vault_dir / "Needs_Action" / filename).exists()


def test_process_routes_to_approval(client, initialized_vault, vault_dir):
    """An urgent email is moved to In_Progress and gets an approval request."""
    filename = _simulate_urgent_email(client)
    resp = client.post("/api/needs-action/process", json={"filename": filename})
    assert "approval" in resp.json()["action"].lower()
    assert (vault_dir / "In_Progress" / filename).exists()
    # There should be an approval file in Pending_Approval
    approval_files = list((vault_dir / "Pending_Approval").glob("APPROVAL_*.md"))
    assert len(approval_files) >= 1
