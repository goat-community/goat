from sqlmodel import SQLModel


class OrganizationBase(SQLModel):
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
