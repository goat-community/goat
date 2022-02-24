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
    "create": {"map": {"zoom": 13, "max_zoom": 21, "min_zoom": 10, "projection_code": "EPSG:3857"}},
    "user_customization_update": {"sport": {"gym": {"icon": "fa-solid fa-dumbbell", "color": ["#985F03"]}}}
}
