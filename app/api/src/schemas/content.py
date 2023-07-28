from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field

from src.db.models.content import Content, ContentBase


content_update_base_example = {
    "name": "Updated content name",
    "description": "Updated content description",
    "tags": ["updated", "content", "tags"],
    "thumbnail_url": "https://updated-content-thumbnail-url.com",
    # TODO: "owner_id": "Updated content owner ID",
}

class ContentType(str, Enum):
    project = "project"
    layer = "layer"
    report = "report"
    style = "style"


class ContentCreate(ContentBase):
    user_id: str | None
    content_type: str | None


class ContentUpdate(ContentBase):
    user_id: str | None

class ContentUpdateBase(BaseModel):
    name: str | None = Field(None, description="Content name")
    description: str | None = Field(None, description="Content description")
    tags: list[str] | None = Field(None, description="Content tags")
    thumbnail_url: str | None = Field(None, description="Content thumbnail URL")
    user_id: UUID | None = Field(None, description="Content owner ID")

# class ContentUpdate(ContentUpdateBase):
#     pass


class ContentRead(Content):
    pass
