from src.db.models.base_class import Base
from sqlalchemy import BigInteger, Column, ForeignKey, SmallInteger
from sqlalchemy.orm import relationship

class ReachedEdgeHeatmapGridCalculation(Base):
    __tablename__ = 'reached_edge_heatmap_grid_calculation'
    __table_args__ = {'schema': 'basic'}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    reached_edge_heatmap_id = Column(ForeignKey('basic.reached_edge_heatmap.id', ondelete='CASCADE'), nullable=False, index=True)
    grid_calculation_id = Column(ForeignKey('basic.grid_calculation.id', ondelete='CASCADE'), nullable=False, index=True)
    start_cost = Column(SmallInteger, nullable=False)
    end_cost = Column(SmallInteger, nullable=False)

    grid_calculation = relationship('GridCalculation')
    reached_edge_heatmap = relationship('ReachedEdgeHeatmap')