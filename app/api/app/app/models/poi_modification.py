from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry

from app.db.base_class import Base

if TYPE_CHECKING:
    from .scenario import Scenario  # noqa: F401


class POIModification(Base):
    __tablename__ = 'poi_modification'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, nullable=True)
    amenity = Column(Text, nullable=True)
    opening_hours = Column(Text, nullable=True)
    wheelchair = Column(Text, nullable=True)
    origin_id = Column(Integer, nullable=True)
    scenario_id = Column(Integer, ForeignKey(
        "scenario.id", ondelete="CASCADE"), nullable=False)
    scenario = relationship("Scenario", back_populates="poi_modification")
    geom = Column(Geometry(geometry_type='POINT', srid='4326'))
