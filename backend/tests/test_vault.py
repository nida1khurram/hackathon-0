def test_vault_status_uninitialized(client, vault_dir):
    """Fresh vault_dir exists but has no folders or core files."""
    resp = client.get("/api/vault/status")
    assert resp.status_code == 200
    data = resp.json()
    # tmp_path exists, so initialized is True (directory exists),
    # but no folders or core files have been created yet.
    for folder in data["folders"]:
        assert folder["count"] == 0
    for cf in data["core_files"]:
        assert cf["exists"] is False


def test_vault_init(client, vault_dir):
    """POST /api/vault/init creates vault successfully."""
    resp = client.post(
        "/api/vault/init",
        json={"owner": "Alice", "business": "Alice Co"},
    )
    assert resp.status_code == 200
    assert "initialized" in resp.json()["message"].lower()


def test_vault_status_after_init(client, initialized_vault):
    """After init, status reports initialized=True and core files exist."""
    resp = client.get("/api/vault/status")
    data = resp.json()
    assert data["initialized"] is True
    existing = {cf["name"] for cf in data["core_files"] if cf["exists"]}
    assert "Dashboard.md" in existing
    assert "Company_Handbook.md" in existing
    assert "Business_Goals.md" in existing


def test_vault_init_creates_folders(client, initialized_vault, vault_dir):
    """All 11 expected vault folders are created on disk."""
    expected = {
        "Inbox", "Needs_Action", "In_Progress", "Plans",
        "Pending_Approval", "Approved", "Rejected", "Done",
        "Logs", "Briefings", "Accounting",
    }
    actual = {p.name for p in vault_dir.iterdir() if p.is_dir()}
    assert expected.issubset(actual)


def test_vault_init_creates_core_files(client, initialized_vault, vault_dir):
    """All 4 core template files exist after init."""
    for name in ["Dashboard.md", "Company_Handbook.md", "Business_Goals.md", ".gitignore"]:
        assert (vault_dir / name).exists(), f"{name} missing"


def test_vault_init_idempotent(client, initialized_vault):
    """Calling init a second time succeeds without error."""
    resp = client.post(
        "/api/vault/init",
        json={"owner": "Test Owner", "business": "Test Biz"},
    )
    assert resp.status_code == 200
