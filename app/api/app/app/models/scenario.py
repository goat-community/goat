from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, Text, ARRAY, Boolean, BIGINT
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Scenario(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text)
    deleted_pois = Column(ARRAY(BIGINT))
    deleted_ways = Column(ARRAY(BIGINT))
    deleted_buildings = Column(ARRAY(BIGINT))
    ways_heatmap_computed = Column(Boolean)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user = relationship("User", back_populates="scenarios")
