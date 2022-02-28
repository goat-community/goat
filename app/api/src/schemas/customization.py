from sqlmodel import SQLModel


class CustomizationBase(SQLModel):
    setting: str


class CustomizationCreate(CustomizationBase):
    pass


class CustomizationUpdate(CustomizationBase):
    pass


"""
Body of the request
"""
request_examples = {
    "create": {
        "map": {"zoom": 13, "max_zoom": 21, "min_zoom": 10, "projection_code": "EPSG:3857"}
    },
    "user_customization_insert": {
        "poi": {
            "summary": "Update POI setting",
            "value": {"nursery": {"icon": "fa-solid fa-dumbbell", "color": ["#ff0000"]}}
        },
        "layer": {
            "summary": "Update Layer Style",
            "value": {
                "accidents_pedestrians": {
                    "name": "accidents_pedestrians",
                    "rules": [
                        {
                            "name": "New Rule",
                            "symbolizers": [
                                {
                                    "kind": "Mark",
                                    "color": "#ff9900",
                                    "radius": 3,
                                    "wellKnownName": "Square",
                                }
                            ],
                        }
                    ],
                }
            }
        }
    },
    "user_customization_delete": {
        "poi": {
            "summary": "Delete POI setting",
            "value": "nursery"
        },
        "layer": {
            "summary": "Delete Layer Style",
            "value": "accidents_pedestrians"
        }
    }
}
