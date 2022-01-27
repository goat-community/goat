from src.db.models.base_class import Base
from sqlalchemy import Column, DateTime, Integer, Text, text

class Organization(Base):
    __tablename__ = 'organization'
    __table_args__ = {'schema': 'customer'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    creation_date = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))