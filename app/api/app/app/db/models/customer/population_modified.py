from app.db.models.base_class import Base
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, text, Index
from sqlalchemy.orm import relationship

from geoalchemy2 import Geometry

class PopulationModified(Base):
    __tablename__ = 'population_modified'
    __table_args__ = {'schema': 'customer'}

    id = Column(Integer, primary_key=True, autoincrement=True))
    building_modified_id = Column(ForeignKey('customer.building_modified.id', ondelete='CASCADE'), nullable=False, index=True)
    scenario_id = Column(ForeignKey('customer.scenario.id', ondelete='CASCADE'), nullable=False, index=True)
    population = Column(Float(53))
    geom = Column(Geometry(geometry_type="Point", srid="4326", spatial_index=False), nullable=False)
    creation_date = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    building_modified = relationship('BuildingModified')
    scenario = relationship('Scenario')

Index('idx_population_modified_geom', PopulationModified.__table__.c.geom, postgresql_using='gist')
