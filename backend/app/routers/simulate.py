from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services import email_simulator

router = APIRouter(prefix="/api/simulate", tags=["simulate"])


class EmailRequest(BaseModel):
    sender: str
    subject: str
    body: str
    type: str = "email"
    priority: str = "normal"


class BatchRequest(BaseModel):
    count: int = 5


@router.post("/email")
def simulate_single_email(request: EmailRequest):
    """Simulate a single incoming email by writing it to Needs_Action."""
    try:
        message, filename = email_simulator.simulate_email(
            sender=request.sender,
            subject=request.subject,
            body=request.body,
            email_type=request.type,
            priority=request.priority,
        )
        return {"message": message, "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch")
def simulate_batch_emails(request: BatchRequest):
    """Generate a batch of random realistic simulated emails."""
    try:
        message, count, files = email_simulator.simulate_batch(count=request.count)
        return {"message": message, "count": count, "files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
