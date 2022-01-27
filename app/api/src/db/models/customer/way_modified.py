from src.db.models.base_class import Base
from sqlalchemy import BigInteger, Boolean, Column, DateTime, Float, ForeignKey, Integer, SmallInteger, Text, text, Index
from sqlalchemy.orm import relationship

from geoalchemy2 import Geometry

class WayModified(Base):
    __tablename__ = 'way_modified'
    __table_args__ = {'schema': 'customer'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    scenario_id = Column(ForeignKey('customer.scenario.id', ondelete='CASCADE'))
    edge_id = Column(ForeignKey('basic.edge.id', ondelete='CASCADE'))
    class_id = Column(Integer, nullable=False)
    way_type = Column(Text)
    edit_type = Column(Text)
    length_m = Column(Float(53), nullable=False)
    name = Column(Text)
    one_way = Column(Integer)
    maxspeed_forward = Column(Integer)
    maxspeed_backward = Column(Integer)
    osm_id = Column(BigInteger)
    bicycle = Column(Text)
    foot = Column(Text)
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
    creation_date = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    edge = relationship('Edge')
    scenario = relationship('Scenario')

Index('idx_way_modified_geom', WayModified.__table__.c.geom, postgresql_using='gist')