from pydantic import BaseModel


class SectionValidation(BaseModel):
    section: str
    description: str
    present: bool


class HandbookData(BaseModel):
    content: str
    validation: list[SectionValidation]
    is_complete: bool


class HandbookUpdate(BaseModel):
    content: str
