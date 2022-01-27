from src.db.models.base_class import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, text
from sqlalchemy.orm import relationship

class UserStudyArea(Base):
    __tablename__ = 'user_study_area'
    __table_args__ = {'schema': 'customer'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(ForeignKey('customer.user.id', ondelete='CASCADE'), nullable=False)
    study_area_id = Column(ForeignKey('basic.study_area.id', ondelete='CASCADE'), nullable=False)
    creation_date = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    study_area = relationship('StudyArea')
    user = relationship('User')