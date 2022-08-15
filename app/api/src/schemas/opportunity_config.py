from random import random
from src.db import models
from src.tests.utils.utils import random_lower_string


class RequestExample:
    @property
    def oportunity_study_area_config(self):
        return {
            "sensitivity": None,
            "multiple_entrance": True,
            "opportunity_group_id": 14,
            "category": "test_" + random_lower_string(),
            "icon": "fas fa-train-subway-tunnel",
            "color": ["#E182A5"],
            "study_area_id": 83110000,
            "is_active": False,
        }


request_examples = RequestExample()


class CreateOpportunityStudyAreaConfig(models.OpportunityStudyAreaConfig):
    class Config:
        schema_extra = {"example": request_examples.oportunity_study_area_config}
