from src.db.models.base_class import Base
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, Text, text
from sqlalchemy.orm import relationship

class IsochroneCalculation(Base):
    __tablename__ = 'isochrone_calculation'
    __table_args__ = {'schema': 'customer'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    calculation_type = Column(Text, nullable=False)
    user_id = Column(ForeignKey('customer.user.id', ondelete='CASCADE'), nullable=False)
    scenario_id = Column(ForeignKey('customer.scenario.id', ondelete='CASCADE'))
    starting_point = Column(Text, nullable=False)
    routing_profile = Column(Text, nullable=False)
    speed = Column(Float(53), nullable=False)
    modus = Column(Text, nullable=False)
    parent_id = Column(ForeignKey('customer.isochrone_calculation.id', ondelete='CASCADE'))
    creation_date = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    parent = relationship('IsochroneCalculation', remote_side=[id])
    scenario = relationship('Scenario')
    user = relationship('User')