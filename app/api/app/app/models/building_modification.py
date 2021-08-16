from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry

from app.db.base_class import Base

if TYPE_CHECKING:
    from .scenario import Scenario  # noqa: F401


class BuildingModification(Base):
    __tablename__ = 'building_modification'
    id = Column(Integer, primary_key=True, index=True)
    building = Column(Integer, nullable=False)
    building_levels = Column(Integer, nullable=False)
    building_levels_residential = Column(Integer, nullable=False)
    gross_floor_area = Column(Integer, nullable=False)
    population = Column(Integer, nullable=False)
    origin_id = Column(Integer, nullable=True)
    scenario_id = Column(Integer, ForeignKey(
        "scenario.id", ondelete="CASCADE"), nullable=False)
    scenario = relationship("Scenario", back_populates="building_modifications")
    geom = Column(Geometry(geometry_type='POLYGON', srid='4326'))
