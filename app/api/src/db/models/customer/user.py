from app.db.models.base_class import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, text
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = 'user'
    __table_args__ = {'schema': 'customer'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    organization_id = Column(ForeignKey('customer.organization.id', ondelete='CASCADE'), nullable=False)
    name = Column(Text, nullable=False)
    surname = Column(Text, nullable=False)
    email = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean)
    is_superuser = Column(Boolean)
    storage = Column(Integer)
    creation_date = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    organization = relationship('Organization')