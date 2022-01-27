from src.db.models.base_class import Base
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

class ReachedPoiHeatmap(Base):
    __tablename__ = 'reached_poi_heatmap'
    __table_args__ = {'schema': 'basic'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    poi_id = Column(ForeignKey('basic.poi.id', ondelete='CASCADE'), nullable=False)
    scenario_id = Column(ForeignKey('customer.scenario.id', ondelete='CASCADE'))
    grid_calculation_id = Column(ForeignKey('basic.grid_calculation.id', ondelete='CASCADE'), nullable=False)
    cost = Column(Integer, nullable=False)

    grid_calculation = relationship('GridCalculation')
    poi = relationship('Poi')
    scenario = relationship('Scenario')