from enum import Enum
from typing import Optional
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


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    state: Optional["RoleState"] = None


class RoleDB(RoleBase):
    role_id: UUID

    class Config:
        orm_mode = True


class ConfigurationBase(BaseModel):
    tenant_id: UUID
    company_name: str


class ConfigurationCreate(ConfigurationBase):
    pass


class ConfigurationUpdate(BaseModel):
    tenant_id: Optional[UUID] = None
    company_name: Optional[str] = None


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


class AuthenticationUpdate(BaseModel):
    user_id: Optional[UUID] = None
    role_id: Optional[UUID] = None
    configuration_id: Optional[UUID] = None
    email: Optional[str] = None
    password: Optional[str] = None


class AuthenticationDB(AuthenticationBase):
    authentication_id: UUID

    class Config:
        orm_mode = True
