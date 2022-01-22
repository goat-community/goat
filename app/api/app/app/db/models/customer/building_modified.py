from app.db.models.base_class import Base
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, SmallInteger, Text, text, Index
from sqlalchemy.orm import relationship

from geoalchemy2 import Geometry

class BuildingModified(Base):
    __tablename__ = 'building_modified'
    __table_args__ = {'schema': 'customer'}

    id = Column(Integer, primary_key=True, autoincrement=True))
    scenario_id = Column(ForeignKey('customer.scenario.id', ondelete='CASCADE'), nullable=False, index=True)
    building_id = Column(ForeignKey('basic.building.id', ondelete='CASCADE'))
    building = Column(Text)
    amenity = Column(Text)
    residential_status = Column(Text)
    housenumber = Column(Text)
    street = Column(Text)
    building_levels = Column(SmallInteger)
    building_levels_residential = Column(SmallInteger)
    roof_levels = Column(SmallInteger)
    height = Column(Float(53))
    area = Column(Integer)
    gross_floor_area_residential = Column(Integer)
    geom = Column(Geometry(geometry_type="Polygon", srid="4326", spatial_index=False), nullable=False)
    creation_date = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    building1 = relationship('Building')
    scenario = relationship('Scenario')

Index('idx_building_modified_geom', BuildingModified.__table__.c.geom, postgresql_using='gist')
