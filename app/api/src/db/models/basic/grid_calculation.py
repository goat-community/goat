from src.db.models.base_class import Base
from sqlalchemy import BigInteger, Column,  ForeignKey, Index
from sqlalchemy.orm import relationship

from geoalchemy2 import Geometry

class GridCalculation(Base):
    __tablename__ = 'grid_calculation'
    __table_args__ = {'schema': 'basic'}

    id = Column(BigInteger, primary_key=True)
    grid_visualization_id = Column(ForeignKey('basic.grid_visualization.id', ondelete='CASCADE'), nullable=False, index=True)
    geom = Column(Geometry(geometry_type="Polygon", srid="4326", spatial_index=False), nullable=False)

    grid_visualization = relationship('GridVisualization')

Index('idx_grid_caclulation_geom', GridCalculation.__table__.c.geom, postgresql_using='gist')