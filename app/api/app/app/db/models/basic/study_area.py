from app.db.models.base_class import Base
from sqlalchemy import Column, Integer, Text, text, Index
from geoalchemy2 import Geometry

class StudyArea(Base):
    __tablename__ = 'study_area'
    __table_args__ = {'schema': 'basic'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    population = Column(Integer, nullable=False)
    geom = Column(Geometry(geometry_type="MultiPolygon", srid="4326", spatial_index=False), nullable=False)

Index('idx_study_area_geom', StudyArea.__table__.c.geom, postgresql_using='gist')