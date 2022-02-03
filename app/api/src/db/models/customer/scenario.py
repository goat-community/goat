from src.db.models.base_class import Base
from sqlalchemy import ARRAY, Boolean, Column, DateTime, ForeignKey, Integer, Text, text
from sqlalchemy.orm import relationship

class Scenario(Base):
    __tablename__ = 'scenario'
    __table_args__ = {'schema': 'customer'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    scenario_name = Column(Text, nullable=False)
    user_id = Column(ForeignKey('customer.user.id', ondelete='CASCADE'), nullable=False)
    deleted_ways = Column(ARRAY(Integer()), server_default=text("'{}'::int[]"))
    deleted_pois = Column(ARRAY(Text()), server_default=text("'{}'::text[]"))
    deleted_buildings = Column(ARRAY(Integer()), server_default=text("'{}'::int[]"))
    routing_heatmap_computed = Column(Boolean)
    creation_date = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    user = relationship('User')
