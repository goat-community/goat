from src.crud.base import CRUDBase
from src.db import models


class CRUDOpportunityGroup(CRUDBase[models.OpportunityGroup, models.OpportunityGroup, models.OpportunityGroup]):
    pass


opportunity_group = CRUDOpportunityGroup(models.OpportunityGroup)


class CRUDOpportunityDefaultConfig(CRUDBase[models.OpportunityDefaultConfig, models.OpportunityDefaultConfig, models.OpportunityDefaultConfig]):
    pass


opportunity_default_config = CRUDOpportunityDefaultConfig(models.OpportunityDefaultConfig)


class CRUDOpportunityStudyAreaConfig(CRUDBase[models.OpportunityStudyAreaConfig, models.OpportunityStudyAreaConfig, models.OpportunityStudyAreaConfig]):
    pass


opportunity_study_area_config = CRUDOpportunityStudyAreaConfig(models.OpportunityStudyAreaConfig)

class CRUDOpportunityUserConfig(CRUDBase[models.OpportunityUserConfig, models.OpportunityUserConfig, models.OpportunityUserConfig]):
    pass


opportunity_user_config = CRUDOpportunityStudyAreaConfig(models.OpportunityUserConfig)

