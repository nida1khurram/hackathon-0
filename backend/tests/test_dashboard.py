def test_dashboard_empty(client, initialized_vault):
    """Fresh vault returns zeroed-out metrics."""
    resp = client.get("/api/dashboard")
    assert resp.status_code == 200
    data = resp.json()
    assert data["needs_action"] == 0
    assert data["pending_approval"] == 0
    assert data["agent_health"] == "Online"


def test_dashboard_reflects_items(client, initialized_vault):
    """Dashboard counts update after simulating emails."""
    client.post("/api/simulate/batch", json={"count": 3})
    data = client.get("/api/dashboard").json()
    assert data["needs_action"] == 3


def test_dashboard_refresh(client, initialized_vault):
    """POST /api/dashboard/refresh succeeds."""
    resp = client.post("/api/dashboard/refresh")
    assert resp.status_code == 200
    assert "refreshed" in resp.json()["message"].lower()


def test_dashboard_refresh_updates_file(client, initialized_vault, vault_dir):
    """After refresh, Dashboard.md is rewritten on disk."""
    client.post("/api/simulate/batch", json={"count": 2})
    client.post("/api/dashboard/refresh")
    content = (vault_dir / "Dashboard.md").read_text(encoding="utf-8")
    # The refreshed dashboard should mention pending actions count
    assert "Pending actions" in content
