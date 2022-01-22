from app.db.models.base_class import Base
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

class ReachedPoiHeatmapAccessibility(Base):
    __tablename__ = 'reached_poi_heatmap_accessibility'
    __table_args__ = {'schema': 'basic'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    reached_poi_heatmap_id = Column(ForeignKey('basic.reached_poi_heatmap.id', ondelete='CASCADE'), nullable=False)
    sensitivity = Column(Integer, nullable=False)
    accessibility_index = Column(Integer, nullable=False)

    reached_poi_heatmap = relationship('ReachedPoiHeatmap')
