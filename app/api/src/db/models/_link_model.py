from uuid import UUID
from sqlmodel import Column, Field, ForeignKey, Integer, SQLModel, text, Text, Boolean, ARRAY
from typing import List

# TODO: Add relations 
class LayerProjectLink(SQLModel, table=True):
    __tablename__ = "layer_project"
    __table_args__ = {"schema": "customer"}

    id: int | None = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    group: str = Field(sa_column=Column(Text, nullable=True), description="Layer group name")
    layer_id: UUID = Field(
        sa_column=Column(Text, ForeignKey("customer.layer.content_id")), description="Layer ID"
    )
    project_id: UUID = Field(
        sa_column=Column(Text, ForeignKey("customer.project.content_id")), description="Project ID"
    )
    active: bool = Field(
        sa_column=Column(Boolean, nullable=False),
        description="Layer is active or not in the project",
    )
    style_id: UUID | None = Field(
        sa_column=Column(Text, ForeignKey("customer.style.content_id"), nullable=True),
        description="Style ID of the layer",
    )
    active_style_rule: List[bool] | None = Field(
        sa_column=Column(ARRAY(Boolean), nullable=True),
        description="Array with the active style rules for the respective style in the style",
    )
    query: str | None = Field(
        sa_column=Column(Text, nullable=True), description="Query to filter the layer data"
    )

class ScenarioScenarioFeatureLink(SQLModel, table=True):
    __tablename__ = "scenario_scenario_feature"
    __table_args__ = {"schema": "customer"}

    id: int | None = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    scenario_id: UUID = Field(
        sa_column=Column(Text, ForeignKey("customer.scenario.id")), description="Scenario ID"
    )
    scenario_feature_id: UUID = Field(
        sa_column=Column(Text, ForeignKey("customer.scenario_feature.id")), description="Scenario Feature ID"
    )
    