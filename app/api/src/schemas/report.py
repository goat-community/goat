from enum import Enum
from uuid import UUID
from pydantic import Field, BaseModel
from typing import List, Optional, TYPE_CHECKING
from db.models.report import Report
from db.models.report import ReportBase
from .content import ContentUpdateBase, ContentType


class ReportDataType(str, Enum):
    """Report export types."""

    pdf = "pdf"
    png = "png"
    # docx = "docx"
    # pptx = "pptx"
    # md = "md"
    html = "html"


class ReportCreate(ReportBase):
    pass


class ReportUpdate(ContentUpdateBase):
    pass


class ReportRead(Report):
    pass


class ReportProject(BaseModel):
    """Base model for styles."""

    id: Optional[UUID] = Field(..., description="Content ID")
    name: Optional[str] = Field(..., description="Content name")
    description: Optional[str] = Field(None, description="Content description")
    tags: Optional[List[str]] = Field(None, description="Content tags")
    thumbnail_url: Optional[str] = Field(..., description="Content thumbnail URL")
    content_type: ContentType = Field(..., description="Content type")
    user_id: UUID = Field(
        ...,
        description="Content owner ID",
    )
    report: dict = Field(..., description="Report object in JSON Format")
