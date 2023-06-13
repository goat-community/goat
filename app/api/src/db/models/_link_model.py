from typing import Optional
from uuid import UUID
from sqlmodel import Column, Field, ForeignKey, Integer, SQLModel, text, Text, Boolean, ARRAY
from typing import List


class LayerProjectLink(SQLModel, table=True):
    __tablename__ = "layer_project"
    __table_args__ = {"schema": "customer"}

    id: Optional[int] = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    style_id: UUID = Field(
        sa_column=Column(Text, ForeignKey("customer.style.id")),
        description="Style ID of the layer",
    )
    layer_id: UUID = Field(
        sa_column=Column(Text, ForeignKey("customer.layer.id")), description="Layer ID"
    )
    project_id: UUID = Field(
        sa_column=Column(Text, ForeignKey("customer.project.id")), description="Project ID"
    )
    active: bool = Field(
        sa_column=Column(Boolean, nullable=False),
        description="Layer is active or not in the project",
    )
    style_id: Optional[UUID] = Field(
        sa_column=Column(Text, ForeignKey("customer.style.id"), nullable=True),
        description="Style ID of the layer",
    )
    active_style_rule: Optional[List[bool]] = Field(
        sa_column=Column(ARRAY(Boolean), nullable=True),
        description="Array with the active style rules for the respective style in the style",
    )
    query: Optional[str] = Field(
        sa_column=Column(Text, nullable=True), description="Query to filter the layer data"
    )
