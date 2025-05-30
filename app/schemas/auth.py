from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class RoleState(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"


class RoleBase(BaseModel):
    name: str
    state: RoleState = RoleState.ACTIVE


class RoleCreate(RoleBase):
    pass


class RoleUpdate(RoleBase):
    pass


class RoleDB(RoleBase):
    role_id: UUID

    class Config:
        orm_mode = True


class ConfigurationBase(BaseModel):
    tenant_id: UUID
    company_name: str


class ConfigurationCreate(ConfigurationBase):
    pass


class ConfigurationUpdate(ConfigurationBase):
    pass


class ConfigurationDB(ConfigurationBase):
    configuration_id: UUID

    class Config:
        orm_mode = True


class AuthenticationBase(BaseModel):
    user_id: UUID
    role_id: UUID
    configuration_id: UUID
    email: str
    password: str


class AuthenticationCreate(AuthenticationBase):
    pass


class AuthenticationUpdate(AuthenticationBase):
    pass


class AuthenticationDB(AuthenticationBase):
    authentication_id: UUID

    class Config:
        orm_mode = True
