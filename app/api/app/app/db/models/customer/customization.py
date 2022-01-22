from app.db.models.base_class import Base
from sqlalchemy import Column, ForeignKey, Integer, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship


class Customization(Base):
    __tablename__ = 'customization'
    __table_args__ = {'schema': 'customer'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(ForeignKey('customer.role.id', ondelete='CASCADE'), nullable=False)
    type = Column(Text, nullable=False)
    default_setting = Column(JSONB(astext_type=Text()), nullable=False)

    role = relationship('Role')
