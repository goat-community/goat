from app.db.models.base_class import Base
from sqlalchemy import BigInteger, Column, Index
from geoalchemy2 import Geometry

class GridVisualization(Base):
    __tablename__ = 'grid_visualization'
    __table_args__ = {'schema': 'basic'}

    id = Column(BigInteger, primary_key=True)
    geom = Column(Geometry(geometry_type="Polygon", srid="4326", spatial_index=False), nullable=False)

Index('idx_grid_visualization_geom', GridVisualization.__table__.c.geom, postgresql_using='gist')
