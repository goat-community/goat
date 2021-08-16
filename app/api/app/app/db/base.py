# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base  # noqa
from app.models.item import Item  # noqa
from app.models.user import User  # noqa
from app.models.isochrone import Isochrone
from app.models.scenario import Scenario
from app.models.poi_modification import POIModification
from app.models.building_modification import BuildingModification
from app.models.way_modification import WayModification
