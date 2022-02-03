from src.db.models.base_class import Base
from sqlalchemy import Column, ForeignKey, Integer, Text, text, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB

from geoalchemy2 import Geometry

class Poi(Base):
    __tablename__ = 'poi'
    __table_args__ = {'schema': 'basic'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(Text, nullable=False, index=True)
    category = Column(Text, nullable=False, index=True)
    name = Column(Text)
    street = Column(Text)
    housenumber = Column(Text)
    zipcode = Column(Text)
    opening_hours = Column(Text)
    wheelchair = Column(Text)
    tags = Column(JSONB(astext_type=Text()))
    geom = Column(Geometry(geometry_type="Point", srid="4326", spatial_index=False), nullable=False)


Index('idx_poi_geom', Poi.__table__.c.geom, postgresql_using='gist')
UniqueConstraint(Poi.__table__.c.uid)