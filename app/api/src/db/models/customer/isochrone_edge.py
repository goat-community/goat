from src.db.models.base_class import Base
from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry

class IsochroneEdge(Base):
    __tablename__ = 'isochrone_edge'
    __table_args__ = {'schema': 'customer'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    edge_id = Column(ForeignKey('basic.edge.id'))
    isochrone_calculation_id = Column(ForeignKey('customer.isochrone_calculation.id', ondelete='CASCADE'), index=True)
    cost = Column(Float(53), nullable=False)
    start_cost = Column(Float(53), nullable=False)
    end_cost = Column(Float(53), nullable=False)
    start_perc = Column(Float(53))
    end_perc = Column(Float(53))
    partial_edge = Column(Boolean)
    geom = Column(Geometry(geometry_type="Linestring", srid="3857", spatial_index=False), nullable=True)

    edge = relationship('Edge')
    isochrone_calculation = relationship('IsochroneCalculation')

