from fastapi import APIRouter, HTTPException

from app.models.vault import VaultStatus, VaultInitRequest
from app.services import vault_service

router = APIRouter(prefix="/api/vault", tags=["vault"])


@router.get("/status", response_model=VaultStatus)
def vault_status():
    """Return the current vault status including folder counts and core file existence."""
    return vault_service.get_vault_status()


@router.post("/init")
def vault_init(request: VaultInitRequest):
    """Initialize the vault with all folders and core template files."""
    try:
        message = vault_service.init_vault(owner=request.owner, business=request.business)
        return {"message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
