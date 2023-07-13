from enum import Enum
from typing import List
from uuid import UUID

from db.models.report import Report, ReportBase
from pydantic import BaseModel, Field

from .content import ContentType, ContentUpdateBase


class ReportExportType(str, Enum):
    pdf = "pdf"
    png = "png"
    html = "html"


class ReportCreate(ReportBase):
    pass


class ReportUpdate(ContentUpdateBase):
    pass


class ReportRead(Report):
    pass


class ReportProject(BaseModel):
    id: UUID | None = Field(..., description="Content ID")
    name: str | None = Field(..., description="Content name")
    description: str | None = Field(None, description="Content description")
    tags: List[str] | None = Field(None, description="Content tags")
    thumbnail_url: str | None = Field(..., description="Content thumbnail URL")
    content_type: ContentType = Field(..., description="Content type")
    user_id: UUID = Field(
        ...,
        description="Content owner ID",
    )
    report: dict = Field(..., description="Report object in JSON Format")
