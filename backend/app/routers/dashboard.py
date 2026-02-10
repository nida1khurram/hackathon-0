from fastapi import APIRouter, HTTPException

from app.models.dashboard import DashboardMetrics
from app.services import dashboard_service

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardMetrics)
def get_dashboard():
    """Get current dashboard metrics computed from vault state."""
    return dashboard_service.get_metrics()


@router.post("/refresh")
def refresh_dashboard():
    """Refresh the Dashboard.md file in the vault with current metrics."""
    try:
        message = dashboard_service.refresh_dashboard()
        return {"message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
