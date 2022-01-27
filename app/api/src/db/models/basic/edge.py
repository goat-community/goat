from src.db.models.base_class import Base
from sqlalchemy import BigInteger, Boolean, Column, Float, ForeignKey, Integer, SmallInteger, Text, text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON
from geoalchemy2 import Geometry

class Edge(Base):
    __tablename__ = 'edge'
    __table_args__ = {'schema': 'basic'}

    id = Column(Integer, primary_key=True)
    scenario_id = Column(ForeignKey('customer.scenario.id'), index=True)
    edge_id = Column(ForeignKey('basic.edge.id'), index=True)
    class_id = Column(Integer, nullable=False)
    length_m = Column(Float(53), nullable=False)
    length_3857 = Column(Float(53), nullable=False)
    name = Column(Text)
    source = Column(ForeignKey('basic.node.id'), index=True)
    target = Column(ForeignKey('basic.node.id'), index=True)
    one_way = Column(Integer)
    maxspeed_forward = Column(Integer)
    maxspeed_backward = Column(Integer)
    osm_id = Column(BigInteger)
    bicycle = Column(Text, index=True)
    foot = Column(Text, index=True)
    oneway = Column(Text)
    crossing = Column(Text)
    one_link_crossing = Column(Boolean)
    crossing_delay_category = Column(SmallInteger)
    bicycle_road = Column(Text)
    cycleway = Column(Text)
    highway = Column(Text)
    incline = Column(Text)
    incline_percent = Column(Integer)
    lanes = Column(Float(53))
    lit = Column(Text)
    lit_classified = Column(Text)
    parking = Column(Text)
    parking_lane_both = Column(Text)
    parking_lane_right = Column(Text)
    parking_lane_left = Column(Text)
    segregated = Column(Text)
    sidewalk = Column(Text)
    sidewalk_both_width = Column(Float(53))
    sidewalk_left_width = Column(Float(53))
    sidewalk_right_width = Column(Float(53))
    smoothness = Column(Text)
    surface = Column(Text)
    wheelchair = Column(Text)
    wheelchair_classified = Column(Text)
    width = Column(Float(53))
    s_imp = Column(Float(53))
    rs_imp = Column(Float(53))
    impedance_surface = Column(Float(53))
    death_end = Column(Integer)
    geom = Column(Geometry(geometry_type="Linestring", srid="4326", spatial_index=False), nullable=False)
    coordinates_3857 = Column(JSON(astext_type=Text()), nullable=False)
    

    edge = relationship('Edge', remote_side=[id])
    scenario = relationship('Scenario')
    node = relationship('Node', primaryjoin='Edge.source == Node.id')
    node1 = relationship('Node', primaryjoin='Edge.target == Node.id')

Index('idx_edge_geom', Edge.__table__.c.geom, postgresql_using='gist')

