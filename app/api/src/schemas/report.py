from enum import Enum
from uuid import UUID

from src.db.models.report import Report
from pydantic import Field
from src.db.models._base_class import ContentBaseAttributes


class ReportExportType(str, Enum):
    pdf = "pdf"
    png = "png"
    html = "html"


class IReportCreate(ContentBaseAttributes):
    project_id: UUID = Field(..., description="Project ID")
    report: dict = Field(..., description="Report object in JSON Format")


class IReportUpdate(ContentBaseAttributes):
    report: dict = Field(..., description="Report object in JSON Format")


class IReportRead(Report):
    pass


request_examples = {
    "get": {
        "ids": ["39e16c27-2b03-498e-8ccc-68e798c64b8d", "e7dcaae4-1750-49b7-89a5-9510bf2761ad"],
    },
    "create": {
        "folder_id": "39e16c27-2b03-498e-8ccc-68e798c64b8d",
        "name": "My first report",
        "description": "This is my first report",
        "tags": ["tag1", "tag2"],
        "thumbnail_url": "https://goat-app-assets.s3.eu-central-1.amazonaws.com/logos/goat_green.png",
        "project_id": "39e16c27-2b03-498e-8ccc-68e798c64b8d",
        "report": {"no_structure": "no_structure"},
    },
    "update": {
        "folder_id": "39e16c27-2b03-498e-8ccc-68e798c64b8d",
        "name": "My updated report",
        "description": "This is my updated report",
        "tags": ["tag1", "tag2"],
        "thumbnail_url": "https://goat-app-assets.s3.eu-central-1.amazonaws.com/logos/goat_green.png",
        "report": {"no_structure": "no_structure"},
    },
}
