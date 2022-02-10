from pydantic import BaseModel


class OrganizationBase(BaseModel):
    name: str


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(OrganizationBase):
    pass


"""
Body of the request
"""
request_examples = {
    "create": {
        "name": "Plan4Better",
    },
    "update": {
        "name": "Plan4Better gmbh",
    },
}
