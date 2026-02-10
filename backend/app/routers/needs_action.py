from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.action_item import ActionItem, ProcessResult
from app.services import file_processor

router = APIRouter(prefix="/api/needs-action", tags=["needs-action"])


class ProcessRequest(BaseModel):
    filename: str


@router.get("", response_model=list[ActionItem])
def list_action_items():
    """List all items in Needs_Action folder, sorted by priority."""
    return file_processor.get_action_items()


@router.post("/process")
def process_single(request: ProcessRequest):
    """Process a single item from Needs_Action."""
    result = file_processor.process_item(request.filename)
    if result.startswith("File not found"):
        raise HTTPException(status_code=404, detail=result)
    return {"action": result}


@router.post("/process-all", response_model=ProcessResult)
def process_all_items():
    """Process all items currently in Needs_Action."""
    return file_processor.process_all()
