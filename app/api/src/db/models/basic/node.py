from app.db.models.base_class import Base
from sqlalchemy import ARRAY, BigInteger, Boolean, Column, ForeignKey, Integer, Text, text, Index
from sqlalchemy.orm import relationship

from geoalchemy2 import Geometry

class Node(Base):
    __tablename__ = 'node'
    __table_args__ = {'schema': 'basic'}

    id = Column(Integer, primary_key=True)
    scenario_id = Column(ForeignKey('customer.scenario.id', ondelete='CASCADE'), index=True)
    osm_id = Column(BigInteger)
    cnt = Column(Integer)
    class_ids = Column(ARRAY(Integer()))
    foot = Column(ARRAY(Text()))
    bicycle = Column(ARRAY(Text()))
    lit_classified = Column(ARRAY(Text()))
    wheelchair_classified = Column(ARRAY(Text()))
    death_end = Column(Boolean, index=True)
    geom = Column(Geometry(geometry_type="Point", srid="4326", spatial_index=False), nullable=False)

    scenario = relationship('Scenario')

Index('idx_node_geom', Node.__table__.c.geom, postgresql_using='gist')