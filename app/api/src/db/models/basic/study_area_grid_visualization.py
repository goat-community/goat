from src.db.models.base_class import Base
from sqlalchemy import Column, ForeignKey, Integer, text
from sqlalchemy.orm import relationship

class StudyAreaGridVisualization(Base):
    __tablename__ = 'study_area_grid_visualization'
    __table_args__ = {'schema': 'basic'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    study_area_id = Column(ForeignKey('basic.study_area.id', ondelete='CASCADE'), nullable=False, index=True)
    grid_visualization_id = Column(ForeignKey('basic.grid_visualization.id', ondelete='CASCADE'), nullable=False, index=True)

    grid_visualization = relationship('GridVisualization')
    study_area = relationship('StudyArea')