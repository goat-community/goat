from app.db.models.base_class import Base
from sqlalchemy import ARRAY, Column, DateTime, ForeignKey, Integer, Text, text
from sqlalchemy.orm import relationship

class DataUpload(Base):
    __tablename__ = 'data_upload'
    __table_args__ = {'schema': 'customer'}

    id = Column(Integer, primary_key=True, autoincrement=True))
    user_id = Column(ForeignKey('customer.user.id', ondelete='CASCADE'), nullable=False)
    data_type = Column(Text, nullable=False)
    upload_type = Column(Text, nullable=False)
    upload_grid_ids = Column(ARRAY(Text()), nullable=False)
    upload_date = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    upload_size = Column(Integer, nullable=False)
    creation_date = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    user = relationship('User')