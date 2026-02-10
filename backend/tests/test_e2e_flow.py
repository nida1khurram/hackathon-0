def test_full_demo_flow(client, vault_dir):
    """End-to-end: init → simulate → list → process → approve/reject → dashboard."""

    # 1. Initialize vault
    resp = client.post(
        "/api/vault/init",
        json={"owner": "Demo Owner", "business": "Demo Biz"},
    )
    assert resp.status_code == 200

    # 2. Simulate emails: one normal, one payment (needs approval), one urgent
    client.post("/api/simulate/email", json={
        "sender": "friend@example.com",
        "subject": "Lunch plans",
        "body": "Let's meet for lunch.",
        "type": "email",
        "priority": "normal",
    })
    payment_fname = client.post("/api/simulate/email", json={
        "sender": "vendor@example.com",
        "subject": "Invoice #5555",
        "body": "Pay $1000.",
        "type": "payment",
        "priority": "normal",
    }).json()["filename"]
    client.post("/api/simulate/email", json={
        "sender": "ops@example.com",
        "subject": "URGENT outage",
        "body": "Systems down, need help immediately!",
        "type": "email",
        "priority": "high",
    })

    # 3. List needs-action items
    items = client.get("/api/needs-action").json()
    assert len(items) == 3

    # 4. Process all
    result = client.post("/api/needs-action/process-all").json()
    assert result["processed"] == 3

    # Needs_Action should be empty
    assert client.get("/api/needs-action").json() == []

    # 5. Check approvals (payment + urgent email = 2 pending)
    approvals = client.get("/api/approvals").json()
    assert len(approvals) == 2

    # 6. Approve the first, reject the second
    first_id = approvals[0]["id"]
    second_id = approvals[1]["id"]

    resp = client.post(f"/api/approvals/{first_id}/approve")
    assert resp.status_code == 200

    resp = client.post(f"/api/approvals/{second_id}/reject")
    assert resp.status_code == 200

    # Pending approvals should be empty
    assert client.get("/api/approvals").json() == []

    # 7. Dashboard metrics should reflect work done
    metrics = client.get("/api/dashboard").json()
    assert metrics["needs_action"] >= 0
    assert metrics["pending_approval"] == 0
    assert metrics["active_plans"] >= 3  # one plan per processed item
    assert metrics["agent_health"] == "Online"

    # 8. Refresh dashboard and verify file is updated
    resp = client.post("/api/dashboard/refresh")
    assert resp.status_code == 200
    assert (vault_dir / "Dashboard.md").exists()
