from uuid import UUID

from pydantic import Field

from src.db.models.style import Style, StyleBase


class StyleCreate(StyleBase):
    pass


class StyleUpdate(StyleBase):
    name: str | None = Field(None, description="Content name")
    description: str | None = Field(None, description="Content description")
    tags: list | None = Field(None, description="Content tags")
    thumbnail_url: str | None = Field(None, description="Content thumbnail URL")
    style: dict | None = Field(None, description="Style object in the geostyler format")
    owner_id: UUID | None = Field(None, description="Content owner ID")


class StyleRead(Style):
    pass
