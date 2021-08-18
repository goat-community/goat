from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry

from app.db.base_class import Base

if TYPE_CHECKING:
    from scenario import Scenario  # noqa: F401


class WayModification(Base):
    __tablename__ = 'way_modification'
    id = Column(Integer, primary_key=True, index=True)
    way_type = Column(Text, nullable=True)
    surface = Column(Text, nullable=True)
    wheelchair = Column(Text, nullable=True)
    lit = Column(Text, nullable=True)
    street_category = Column(Text, nullable=True)
    foot = Column(Text, nullable=True)
    edit_type = Column(Text, nullable=True)
    bicycle = Column(Text, nullable=True)
    origin_id = Column(Integer, nullable=True)
    status = Column(Integer, nullable=True)
    scenario_id = Column(Integer, ForeignKey(
        "scenario.id", ondelete="CASCADE"), nullable=False)
    scenario = relationship("Scenario", back_populates="way_modification")
    geom = Column(Geometry(geometry_type='POINT', srid='4326'))
