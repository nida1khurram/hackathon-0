from pydantic import BaseModel


class ActionItem(BaseModel):
    id: str
    filename: str
    type: str
    sender: str
    subject: str
    priority: str
    received: str
    status: str
    snippet: str = ""


class ProcessResult(BaseModel):
    processed: int
    actions: list[str]
