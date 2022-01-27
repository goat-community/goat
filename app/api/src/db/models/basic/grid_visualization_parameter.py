from src.db.models.base_class import Base
from sqlalchemy import Column, Float, ForeignKey, Integer, SmallInteger

class GridVisualizationParameter(Base):
    __tablename__ = 'grid_visualization_parameter'
    __table_args__ = {'schema': 'basic'}

    id = Column(ForeignKey('basic.grid_visualization.id', ondelete='CASCADE'), primary_key=True)
    area_isochrone = Column(Float(53))
    percentile_area_isochrone = Column(SmallInteger, nullable=False)
    population = Column(Integer)
    percentile_population = Column(SmallInteger, nullable=False)
