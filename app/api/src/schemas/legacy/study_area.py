from pydantic import BaseModel, validator
from typing import Optional, List, Dict
from src import crud
from src.db.session import sync_session


groups_example_data = """
{
  "layer_groups": [
    {
      "buildings_landuse": [
        "building",
        "landuse_atkis",
        "landuse_osm"
      ]
    },
    {
      "environmental_quality": [
        "bayern_laerm_ballungszentren_strassen_tag",
        "bayern_laerm_ballungszentren_strassen_nacht",
        "bayern_oekoflaechenkataster",
        "bayern_schutzgebiete_naturschutz",
        "bayern_biotop_kartierung"
      ]
    },
    {
      "additional_data": [
        "accidents_pedestrians",
        "accidents_cyclists"
      ]
    }
  ]
}
"""

GROUP_ORDER = [
    "buildings_landuse",
    "street_level_quality",
    "environmental_quality",
    "additional_data",
    "basemap",
    "heatmap",
    "indicator",
]


# Used for output, Doesn't fetch database
class LayerGroupBase(BaseModel):
    buildings_landuse: Optional[List[str]] = []
    street_level_quality: Optional[List[str]] = []
    environmental_quality: Optional[List[str]] = []
    additional_data: Optional[List[str]] = []
    basemap: Optional[List[str]] = []
    heatmap: Optional[List[str]] = []
    indicator: Optional[List[str]] = []

    def listify_config(self) -> Dict:
        """
        Convert me to listing config to save into databse
        """
        out_config = []
        for group in GROUP_ORDER:
            value = getattr(self, group)
            if value:
                out_config.append({group: value})
        return out_config


# Used for output, Doesn't fetch database
class StudyAreaSettingsBase(BaseModel):
    layer_groups: List[LayerGroupBase]


class LayerGroup(LayerGroupBase):
    @validator("buildings_landuse")
    def validate_layer_names(cls, v):
        """
        Check if layers are in available layer libraries
        """
        valid_layers = cls.get_valid_layers()
        for layer_name in v:
            if layer_name not in valid_layers:
                raise ValueError(f"layer {layer_name} is not a valid layer")

        return v

    @classmethod
    def get_valid_layers(cls):
        """
        Fetch corrently available layer libraries
        """
        if hasattr(cls, "valid_layers"):
            return cls.valid_layers
        else:
            cls.valid_layers = crud.layer_library.get_all_layer_names(db=sync_session())
            return cls.valid_layers


class StudyAreaSettings(BaseModel):
    layer_groups: List[LayerGroup]


def pydantify_config(in_config: Dict, validate: bool = True) -> LayerGroup:
    """
    Convert database-saved config into Pydantic (Remove listing)
    """
    temp_config = {}
    for group in in_config.get("layer_groups"):
        for key in group.keys():
            temp_config[key] = group[key]

    LayerGroup_ = LayerGroup
    if not validate:
        LayerGroup_ = LayerGroupBase
    out_config = LayerGroup_(**temp_config)
    return out_config
