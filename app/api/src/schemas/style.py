from pydantic import Field
from uuid import UUID
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Column, text, ForeignKey, Text, Relationship, SQLModel
from typing import List, Optional, Union, TYPE_CHECKING
from sqlalchemy.orm import relationship
from src.db.models.style import StyleBase, Style


class StyleCreate(StyleBase):
    pass


class StyleUpdate(StyleBase):
    name: Optional[str] = Field(None, description="Content name")
    description: Optional[str] = Field(None, description="Content description")
    tags: Optional[list] = Field(None, description="Content tags")
    thumbnail_url: Optional[str] = Field(None, description="Content thumbnail URL")
    style: Optional[dict] = Field(None, description="Style object in the geostyler format")
    owner_id: Optional[UUID] = Field(None, description="Content owner ID")


class StyleRead(Style):
    pass
