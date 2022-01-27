from src.db.models.base_class import Base
from sqlalchemy import  Column, DateTime, ForeignKey, Text, text, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from geoalchemy2 import Geometry

class AoiModified(Base):
    __tablename__ = 'aoi_modified'
    __table_args__ = {'schema': 'customer'}

    id = Column(ForeignKey('basic.aoi.id', ondelete='CASCADE'), primary_key=True, autoincrement=True)
    scenario_id = Column(ForeignKey('customer.scenario.id', ondelete='CASCADE'), index=True)
    category = Column(Text, nullable=False, index=True)
    name = Column(Text)
    opening_hours = Column(Text)
    wheelchair = Column(Text)
    tags = Column(JSONB(astext_type=Text()))
    geom = Column(Geometry(geometry_type="MultiPolygon", srid="4326", spatial_index=False), nullable=False)
    creation_date = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    scenario = relationship('Scenario')

Index('idx_aoi_modified_geom', AoiModified.__table__.c.geom, postgresql_using='gist')
