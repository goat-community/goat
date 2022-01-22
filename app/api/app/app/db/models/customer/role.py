from app.db.models.base_class import Base
from sqlalchemy import Column, Integer, Text, text

class Role(Base):
    __tablename__ = 'role'
    __table_args__ = {'schema': 'customer'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)