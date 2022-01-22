from app.db.models.base_class import Base
from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

class IsochroneEdge(Base):
    __tablename__ = 'isochrone_edge'
    __table_args__ = {'schema': 'customer'}

    id = Column(Integer, primary_key=True, autoincrement=True))
    edge_id = Column(ForeignKey('basic.edge.id'))
    isochrone_calculation_id = Column(ForeignKey('customer.isochrone_calculation.id', ondelete='CASCADE'), index=True)
    cost = Column(Float(53))
    start_cost = Column(Float(53))
    end_cost = Column(Float(53))
    partial_edge = Column(Boolean)

    edge = relationship('Edge')
    isochrone_calculation = relationship('IsochroneCalculation')

