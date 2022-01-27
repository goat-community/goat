from src.db.models.base_class import Base
from sqlalchemy import Column, Float, ForeignKey, Integer, SmallInteger, Text, text, Index
from sqlalchemy.orm import relationship

from geoalchemy2 import Geometry

class Building(Base):
    __tablename__ = 'building'
    __table_args__ = {'schema': 'basic'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    scenario_id = Column(ForeignKey('customer.scenario.id', ondelete='CASCADE'))
    osm_id = Column(Integer)
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

    scenario = relationship('Scenario')

Index('idx_building_geom', Building.__table__.c.geom, postgresql_using='gist')