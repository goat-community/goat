from src.db.models.base_class import Base
from sqlalchemy import Column, ForeignKey, Integer, Text, text, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from geoalchemy2 import Geometry

class IsochroneFeature(Base):
    __tablename__ = 'isochrone_feature'
    __table_args__ = {'schema': 'customer'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    isochrone_calculation_id = Column(ForeignKey('customer.isochrone_calculation.id', ondelete='CASCADE'), nullable=False, index=True)
    step = Column(Integer, nullable=False)
    reached_opportunities = Column(JSONB(astext_type=Text()))
    geom = Column(Geometry(geometry_type="MultiPolygon", srid="4326", spatial_index=False), nullable=False)

    isochrone_calculation = relationship('IsochroneCalculation')

Index('idx_isochrone_feature_geom', IsochroneFeature.__table__.c.geom, postgresql_using='gist')