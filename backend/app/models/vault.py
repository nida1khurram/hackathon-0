from pydantic import BaseModel


class FolderStatus(BaseModel):
    name: str
    count: int


class CoreFileStatus(BaseModel):
    name: str
    exists: bool


class VaultStatus(BaseModel):
    initialized: bool
    folders: list[FolderStatus]
    core_files: list[CoreFileStatus]


class VaultInitRequest(BaseModel):
    owner: str = "AI Employee"
    business: str = "My Business"
