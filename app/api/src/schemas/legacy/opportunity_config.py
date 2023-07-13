from src.db import models
from src.legacy.utils.utils import random_lower_string
from src.crud.crud_study_area import study_area as crud_study_area
from src.crud.crud_opportunity_config import opportunity_group as crud_opportunity_group


class RequestExample:
    @property
    def oportunity_study_area_config(self):
        return {
            "sensitivity": None,
            "multiple_entrance": True,
            "opportunity_group_id": 12,
            "category": "test_" + random_lower_string(),
            "icon": "fas fa-train-subway-tunnel",
            "color": ["#E182A5"],
            "study_area_id": 83110000,
            "is_active": False,
        }

    async def async_oportunity_study_area_config(self, db):
        study_area = await crud_study_area.get_first(db=db)
        if not study_area:
            raise ValueError("There is no study area available")
        opportunity_groups = await crud_opportunity_group.get_all(db=db)
        if opportunity_groups:
            opportunity_group = opportunity_groups[0]
        else:
            raise ValueError("There is no opportunity group available")
        return {
            "sensitivity": None,
            "multiple_entrance": True,
            "opportunity_group_id": opportunity_group.id,
            "category": "test_" + random_lower_string(),
            "icon": "fas fa-train-subway-tunnel",
            "color": ["#E182A5"],
            "study_area_id": study_area.id,
            "is_active": False,
        }


request_examples = RequestExample()


class CreateOpportunityStudyAreaConfig(models.OpportunityStudyAreaConfig):
    class Config:
        schema_extra = {"example": request_examples.oportunity_study_area_config}
