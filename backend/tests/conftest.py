import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app


@pytest.fixture(autouse=True)
def vault_dir(tmp_path, monkeypatch):
    """Point settings.vault_dir to a fresh temp directory for every test."""
    monkeypatch.setattr(
        type(settings), "vault_dir", property(lambda self: tmp_path)
    )
    return tmp_path


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def initialized_vault(client):
    """Call vault init so tests start with a ready vault."""
    resp = client.post(
        "/api/vault/init",
        json={"owner": "Test Owner", "business": "Test Biz"},
    )
    assert resp.status_code == 200
    return resp.json()
