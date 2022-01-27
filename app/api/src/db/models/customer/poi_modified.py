from src.db.models.base_class import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, text, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from geoalchemy2 import Geometry

class PoiModified(Base):
    __tablename__ = 'poi_modified'
    __table_args__ = {'schema': 'customer'}

    id = Column(ForeignKey('basic.poi.id', ondelete='CASCADE'), primary_key=True, autoincrement=True)
    scenario_id = Column(ForeignKey('customer.scenario.id', ondelete='CASCADE'), index=True)
    poi_id = Column(Integer, index=True)
    poi_user_id = Column(ForeignKey('customer.poi_user.id', ondelete='CASCADE'), index=True)
    category = Column(Text, nullable=False)
    name = Column(Text)
    street = Column(Text)
    housenumber = Column(Text)
    zipcode = Column(Text)
    opening_hours = Column(Text)
    wheelchair = Column(Text)
    tags = Column(JSONB(astext_type=Text()))
    geom = Column(Geometry(geometry_type="Point", srid="4326", spatial_index=False), nullable=False)
    creation_date = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    poi_user = relationship('PoiUser')
    scenario = relationship('Scenario')

Index('idx_poi_modified_geom', PoiModified.__table__.c.geom, postgresql_using='gist')

