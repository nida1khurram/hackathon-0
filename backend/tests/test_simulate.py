def test_simulate_single_email(client, initialized_vault):
    """POST /api/simulate/email returns 200 with filename."""
    resp = client.post("/api/simulate/email", json={
        "sender": "bob@example.com",
        "subject": "Hello",
        "body": "Just a test email",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "filename" in data
    assert data["filename"].startswith("EMAIL_")
    assert data["filename"].endswith(".md")


def test_simulate_email_creates_file(client, initialized_vault, vault_dir):
    """Simulated email file appears on disk in Needs_Action."""
    resp = client.post("/api/simulate/email", json={
        "sender": "bob@example.com",
        "subject": "Test",
        "body": "body",
    })
    filename = resp.json()["filename"]
    assert (vault_dir / "Needs_Action" / filename).exists()


def test_simulate_batch(client, initialized_vault):
    """POST /api/simulate/batch returns expected count and file list."""
    resp = client.post("/api/simulate/batch", json={"count": 3})
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 3
    assert len(data["files"]) == 3


def test_simulate_batch_files_on_disk(client, initialized_vault, vault_dir):
    """Batch-generated files actually exist in Needs_Action."""
    resp = client.post("/api/simulate/batch", json={"count": 4})
    for fname in resp.json()["files"]:
        assert (vault_dir / "Needs_Action" / fname).exists()
