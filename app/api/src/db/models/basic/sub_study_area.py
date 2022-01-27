from src.db.models.base_class import Base
from sqlalchemy import Column, Float, ForeignKey, Integer, SmallInteger, Text, text, Index
from sqlalchemy.orm import relationship

from geoalchemy2 import Geometry

class SubStudyArea(Base):
    __tablename__ = 'sub_study_area'
    __table_args__ = {'schema': 'basic'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    study_area_id = Column(ForeignKey('basic.study_area.id'), nullable=False, index=True)
    name = Column(Text, nullable=False)
    population = Column(Integer, nullable=False)
    default_building_levels = Column(SmallInteger)
    default_roof_levels = Column(SmallInteger)
    area = Column(Float(53))
    geom = Column(Geometry(geometry_type="MultiPolygon", srid="4326", spatial_index=False), nullable=False)

    study_area = relationship('StudyArea')

Index('idx_sub_study_area_geom', SubStudyArea.__table__.c.geom, postgresql_using='gist')