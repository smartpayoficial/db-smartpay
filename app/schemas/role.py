from uuid import UUID

from pydantic import BaseModel


class RoleBase(BaseModel):
    name: str
    description: str


class RoleCreate(RoleBase):
    pass


class RoleUpdate(RoleBase):
    pass


class RoleDB(RoleBase):
    role_id: UUID

    class Config:
        orm_mode = True
