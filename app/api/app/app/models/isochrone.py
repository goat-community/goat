from typing import TYPE_CHECKING

from geoalchemy2 import Geometry
from sqlalchemy import Column, Integer, Text

from app.db.base_class import Base

class Isochrones(Base):
    __table_name__ = "isochrones"
    id = Column(Integer, primary_key=True, index=True)
    step = Column(Integer, nullable=False)
    speed = Column(Integer, nullable=False)
    modus = Column(Integer, nullable=False)
    objectid = Column(Integer, nullable=False)
    parent_id = Column(Integer, nullable=False)
    population = Column(Integer, nullable=False)
    concavity = Column(Integer, nullable=False)
    pois = Column(Text)
    sum_pois_time = Column(Text)
    sum_pois = Column(Text)
    starting_point = Column(Text, nullable=False)
    scenario_id = Column(Integer, nullable=False)
    userid = Column(Integer, nullable=False)
    geom = Column(Geometry(geometry_type="GEOMETRY", srid="4326"))
