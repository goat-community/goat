# Import all the models, so that Base has them before being
# imported by Alembic
from src.db.models.base_class import Base  

from .aoi_modified import AoiModified as AoiModifiedDB
from .aoi_user import AoiUser as AoiUserDB
from .building_modified import BuildingModified as BuildingModifiedDB 
from .customization import Customization as CustomizationDB
from .data_upload import DataUpload as DataUploadDB
from .isochrone_calculation import IsochroneCalculation as IsochroneCalculationDB
from .isochrone_edge import IsochroneEdge as IsochroneEdgeDB
from .isochrone_feature import IsochroneFeature as IsochroneFeatureDB
from .organization import Organization as OrganizationDB
from .poi_modified import PoiModified as PoiModifiedDB
from .poi_user import PoiUser as PoiUserDB
from .population_modified import PopulationModified as PopulationModifiedDB
from .role import Role as RoleDB
from .scenario import Scenario as ScenarioDB
from .user_customization import UserCustomization as UserCustomizationDB
from .user_study_area import UserStudyArea as UserStudyAreaDB
from .user import User as UserDB
from .way_modified import WayModified as WayModifiedDB