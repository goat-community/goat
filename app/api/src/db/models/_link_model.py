from uuid import UUID
from sqlmodel import Column, Field, ForeignKey, Integer, SQLModel, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as UUID_PG, JSONB
from src.db.models._base_class import DateTimeBase

# TODO: Add relations
class LayerProjectLink(DateTimeBase, table=True):
    __tablename__ = "layer_project"
    __table_args__ = {"schema": "customer"}

    id: int | None = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    group: str = Field(sa_column=Column(Text, nullable=True), description="Layer group name")
    layer_id: UUID = Field(
        sa_column=Column(UUID_PG(as_uuid=True), ForeignKey("customer.layer.id")),
        description="Layer ID",
    )
    project_id: UUID = Field(
        sa_column=Column(UUID_PG(as_uuid=True), ForeignKey("customer.project.id")),
        description="Project ID",
    )
    active: bool = Field(
        sa_column=Column(Boolean, nullable=False),
        description="Layer is active or not in the project",
    )
    style: dict | None = Field(
        sa_column=Column(JSONB, nullable=True),
        description="Style of the layer",
    )
    query: str | None = Field(
        sa_column=Column(Text, nullable=True), description="Query to filter the layer data"
    )


class ScenarioScenarioFeatureLink(DateTimeBase, table=True):
    __tablename__ = "scenario_scenario_feature"
    __table_args__ = {"schema": "customer"}

    id: int | None = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    scenario_id: UUID = Field(
        sa_column=Column(UUID_PG(as_uuid=True), ForeignKey("customer.scenario.id")),
        description="Scenario ID",
    )
    scenario_feature_id: UUID = Field(
        sa_column=Column(UUID_PG(as_uuid=True), ForeignKey("customer.scenario_feature.id")),
        description="Scenario Feature ID",
    )
