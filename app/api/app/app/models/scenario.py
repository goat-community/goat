from app.models import poi_modification
from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, Text, ARRAY, Boolean, BIGINT
from sqlalchemy.orm import relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from .user import User  # noqa: F401
    from .poi_modification import POIModification  # noqa: F401
    from .way_modification import WayModification  # noqa: F401
    from .building_modification import BuildingModification  # noqa: F401


class Scenario(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text)
    deleted_pois = Column(ARRAY(BIGINT))
    deleted_ways = Column(ARRAY(BIGINT))
    deleted_buildings = Column(ARRAY(BIGINT))
    ways_heatmap_computed = Column(Boolean)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="scenario")
    poi_modification = relationship("POIModification", back_populates="scenario")
    way_modification = relationship("WayModification", back_populates="scenario")
    building_modification = relationship(
        "BuildingModification", back_populates="scenario")
