from src.db import models


request_examples = {
    "opportunity_study_area_config": {
        "sensitivity": None,
        "multiple_entrance": True,
        "opportunity_group_id": 14,
        "category": "subway_entrance",
        "icon": "fas fa-train-subway-tunnel",
        "color": ["#E182A5"],
        "study_area_id": 83110000,
        "is_active": False,
    }
}


class CreateOpportunityStudyAreaConfig(models.OpportunityStudyAreaConfig):
    class Config:
        schema_extra = {"example": request_examples["opportunity_study_area_config"]}
