import pytest


def _create_approvable_item(client):
    """Simulate a payment email and process it so it lands in Pending_Approval.
    Returns the approval id."""
    # Payment type always needs approval
    resp = client.post("/api/simulate/email", json={
        "sender": "vendor@example.com",
        "subject": "Invoice #9999",
        "body": "Please pay $500.",
        "type": "payment",
        "priority": "normal",
    })
    filename = resp.json()["filename"]
    client.post("/api/needs-action/process", json={"filename": filename})
    # Fetch the approval
    approvals = client.get("/api/approvals").json()
    assert len(approvals) >= 1
    return approvals[0]["id"], filename


# ── Tests ─────────────────────────────────────────────────────────────────

def test_list_empty(client, initialized_vault):
    """No approvals when vault is fresh."""
    resp = client.get("/api/approvals")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_after_processing(client, initialized_vault):
    """Approvals appear after processing an item that needs approval."""
    _create_approvable_item(client)
    approvals = client.get("/api/approvals").json()
    assert len(approvals) == 1
    assert approvals[0]["status"] == "pending"


def test_approve_item(client, initialized_vault):
    """Approving moves the approval file to Approved."""
    approval_id, _ = _create_approvable_item(client)
    resp = client.post(f"/api/approvals/{approval_id}/approve")
    assert resp.status_code == 200
    assert "approved" in resp.json()["message"].lower()
    # Pending list should now be empty
    assert client.get("/api/approvals").json() == []


def test_reject_item(client, initialized_vault):
    """Rejecting moves the approval file to Rejected."""
    approval_id, _ = _create_approvable_item(client)
    resp = client.post(f"/api/approvals/{approval_id}/reject")
    assert resp.status_code == 200
    assert "rejected" in resp.json()["message"].lower()
    assert client.get("/api/approvals").json() == []


def test_approve_not_found(client, initialized_vault):
    """Approving a non-existent id returns 404."""
    resp = client.post("/api/approvals/nonexistent/approve")
    assert resp.status_code == 404


def test_approve_moves_source_to_done(client, initialized_vault, vault_dir):
    """After approval the source email file ends up in Done."""
    approval_id, email_filename = _create_approvable_item(client)
    client.post(f"/api/approvals/{approval_id}/approve")
    assert (vault_dir / "Done" / email_filename).exists()
    assert not (vault_dir / "In_Progress" / email_filename).exists()
