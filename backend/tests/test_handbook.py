import pytest


def test_get_handbook(client, initialized_vault):
    """GET /api/handbook returns content with validation after init."""
    resp = client.get("/api/handbook")
    assert resp.status_code == 200
    data = resp.json()
    assert "content" in data
    assert "validation" in data
    assert "is_complete" in data


def test_handbook_not_found(client):
    """GET /api/handbook returns 404 when vault is not initialized."""
    resp = client.get("/api/handbook")
    assert resp.status_code == 404


def test_handbook_validation_complete(client, initialized_vault):
    """Default template has all 8 required sections."""
    data = client.get("/api/handbook").json()
    assert data["is_complete"] is True
    assert all(v["present"] for v in data["validation"])


def test_update_handbook(client, initialized_vault):
    """PUT /api/handbook updates the file."""
    new_content = "# My Custom Handbook\n\nNo sections here."
    resp = client.put("/api/handbook", json={"content": new_content})
    assert resp.status_code == 200
    # Read back to confirm
    data = client.get("/api/handbook").json()
    assert data["content"] == new_content


def test_validate_handbook(client, initialized_vault):
    """POST /api/handbook/validate returns validation data."""
    resp = client.post("/api/handbook/validate")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["validation"]) == 8


def test_handbook_missing_sections(client, initialized_vault):
    """After writing incomplete content, validation reports missing sections."""
    client.put("/api/handbook", json={"content": "# Only a title"})
    data = client.post("/api/handbook/validate").json()
    assert data["is_complete"] is False
    missing = [v for v in data["validation"] if not v["present"]]
    assert len(missing) == 8
