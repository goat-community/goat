from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry

from app.db.base_class import Base

if TYPE_CHECKING:
    from .scenario import Scenario  # noqa: F401
    from .user import User  # noqa: F401


class Isochrone(Base):
    __table_name__ = 'isochrone'
    id = Column(Integer, primary_key=True, index=True)
    step = Column(Integer, nullable=False)
    speed = Column(Integer, nullable=False)
    modus = Column(Integer, nullable=False)
    object_id = Column(Integer, nullable=False)
    parent_id = Column(Integer, nullable=False)
    population = Column(Integer, nullable=False)
    concavity = Column(Integer, nullable=False)
    pois = Column(Text)
    sum_pois_time = Column(Text)
    sum_pois = Column(Text)
    starting_point = Column(Text, nullable=False)
    scenario_id = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user = relationship("User", back_populates="isochrones")
    geom = Column(Geometry(geometry_type='POLYGON', srid='4326'))
