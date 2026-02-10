from pydantic import BaseModel


class DashboardMetrics(BaseModel):
    needs_action: int
    pending_approval: int
    done_today: int
    active_plans: int
    mtd_revenue: str
    monthly_target: str
    alerts: list[str]
    recent_activity: list[str]
    agent_health: str = "Online"
