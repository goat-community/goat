from app.db.models.base_class import Base
from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, text, Index
from sqlalchemy.orm import relationship

from geoalchemy2 import Geometry

class ReachedEdgeHeatmap(Base):
    __tablename__ = 'reached_edge_heatmap'
    __table_args__ = {'schema': 'basic'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    edge_id = Column(ForeignKey('basic.edge.id', ondelete='CASCADE'), nullable=False, index=True)
    scenario_id = Column(ForeignKey('customer.scenario.id', ondelete='CASCADE'), index=True)
    start_perc = Column(Float(53), nullable=False)
    end_perc = Column(Float(53), nullable=False)
    partial_edge = Column(Boolean, nullable=False)
    geom = Column(Geometry(geometry_type="Linestring", srid="4326", spatial_index=False), nullable=False)

    edge = relationship('Edge')
    scenario = relationship('Scenario')

Index('idx_reached_edge_heatmap_geom', ReachedEdgeHeatmap.__table__.c.geom, postgresql_using='gist')