from src.db.models.base_class import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

class UserCustomization(Base):
    __tablename__ = 'user_customization'
    __table_args__ = {'schema': 'customer'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(ForeignKey('customer.user.id', ondelete='CASCADE'), nullable=False)
    customization_id = Column(ForeignKey('customer.customization.id', ondelete='CASCADE'), nullable=False)
    setting = Column(JSONB(astext_type=Text()), nullable=False)
    creation_date = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    customization = relationship('Customization')
    user = relationship('User')
