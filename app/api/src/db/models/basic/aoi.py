from src.db.models.base_class import Base
from sqlalchemy import Column, ForeignKey, Integer,  Text, text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB

from geoalchemy2 import Geometry

class Aoi(Base):
    __tablename__ = 'aoi'
    __table_args__ = {'schema': 'basic'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    aoi_id = Column(ForeignKey('basic.aoi.id', ondelete='CASCADE'))
    scenario_id = Column(ForeignKey('customer.scenario.id', ondelete='CASCADE'), index=True)
    category = Column(Text, nullable=False, index=True)
    name = Column(Text)
    opening_hours = Column(Text)
    wheelchair = Column(Text)
    tags = Column(JSONB(astext_type=Text()))
    geom = Column(Geometry(geometry_type="MultiPolygon", srid="4326", spatial_index=False), nullable=False)

    aoi = relationship('Aoi', remote_side=[id])
    scenario = relationship('Scenario')

Index('idx_aoi_geom', Aoi.__table__.c.geom, postgresql_using='gist')