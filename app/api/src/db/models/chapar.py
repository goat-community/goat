import enum
from typing import Optional

from sqlmodel import BigInteger, Enum, Field, ForeignKey, Integer, SQLModel, String


class DataMatchModes(str, enum.Enum):
    mtc = "Matched"
    upd = "Update"
    ins = "Insert"
    dpr = "Deprecated"


class DataFlow(SQLModel, table=True):
    __table_args__ = {"schema": "chapar"}
    __tablename__ = "data_flow"
    id: int = Field(primary_key=True)
    source_table_name: str = Field(String(65))
    target_table_name: str = Field(String(65))
    find_matches_finished: bool = Field(default=False)
    find_updates_finished: bool = Field(default=False)
    find_adds_finished: bool = Field(default=False)
    find_deprecations_finished: bool = Field(default=False)


class DataMatch(SQLModel, table=True):
    __table_args__ = {"schema": "chapar"}
    __tablename__ = "data_match"
    id: int = Field(primary_key=True)
    data_flow_id: int = Field(ForeignKey(DataFlow.id))
    source_data_id: Optional[int] = Field(BigInteger(), nullable=True)
    target_data_id: Optional[int] = Field(BigInteger(), nullable=True)
    comparison_mode: str = Field(Enum(DataMatchModes))
