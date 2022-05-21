from sqlmodel import SQLModel


class RoleBase(SQLModel):
    name: str


class RoleCreate(RoleBase):
    pass


class RoleUpdate(RoleBase):
    pass


"""
Body of the request
"""
request_examples = {
    "create": {
        "name": "role_test",
    },
    "update": {
        "name": "role_update",
    },
}
