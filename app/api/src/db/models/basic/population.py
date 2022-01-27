from src.db.models.base_class import Base
from sqlalchemy import Column, Float, ForeignKey, Integer, Text, text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB

from geoalchemy2 import Geometry

class Population(Base):
    __tablename__ = 'population'
    __table_args__ = {'schema': 'basic'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    building_id = Column(ForeignKey('basic.building.id', ondelete='CASCADE'), index=True)
    scenario_id = Column(ForeignKey('customer.scenario.id', ondelete='CASCADE'), index=True)
    population = Column(Float(53))
    demography = Column(JSONB(astext_type=Text()))
    geom = Column(Geometry(geometry_type="Point", srid="4326", spatial_index=False), nullable=False)

    building = relationship('Building')
    scenario = relationship('Scenario')

Index('idx_population_geom', Population.__table__.c.geom, postgresql_using='gist')

