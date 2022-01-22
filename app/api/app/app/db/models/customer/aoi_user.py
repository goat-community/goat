from app.db.models.base_class import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, text, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from geoalchemy2 import Geometry

class AoiUser(Base):
    __tablename__ = 'aoi_user'
    __table_args__ = {'schema': 'customer'}

    id = Column(Integer, primary_key=True, autoincrement=True))
    data_upload_id = Column(ForeignKey('customer.data_upload.id', ondelete='CASCADE'), nullable=False, index=True)
    scenario_id = Column(ForeignKey('customer.scenario.id', ondelete='CASCADE'))
    aoi_user_id = Column(Integer)
    category = Column(Text, nullable=False, index=True)
    name = Column(Text)
    opening_hours = Column(Text)
    wheelchair = Column(Text)
    tags = Column(JSONB(astext_type=Text()))
    geom = Column(Geometry(geometry_type="MultiPolygon", srid="4326", spatial_index=False), nullable=False)
    creation_date = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    data_upload = relationship('DataUpload')
    scenario = relationship('Scenario')

Index('idx_aoi_user_geom', AoiUser.__table__.c.geom, postgresql_using='gist')

