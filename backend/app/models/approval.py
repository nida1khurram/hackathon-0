from pydantic import BaseModel


class Approval(BaseModel):
    id: str
    filename: str
    action: str
    source_file: str
    created: str
    expires: str
    status: str
    priority: str
    subject: str
    reason: str


class ApprovalAction(BaseModel):
    action: str  # "approve" or "reject"
