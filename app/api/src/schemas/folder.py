from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional

class FolderBase(BaseModel):
    name: str = Field(..., description="Folder name")


class FolderCreate(FolderBase):
    user_id: UUID | None = Field(None, description="Folder owner ID")


class FolderUpdate(FolderBase):
    pass


class FolderRead(FolderBase):
    id: UUID = Field(..., description="Folder ID")
    user_id: UUID = Field(..., description="Folder owner ID")


# Body of request examples

request_examples = {
    "create": {
        "name": "First folder",
    },
    "update": {
        "name": "Better folder name",
    },
}
