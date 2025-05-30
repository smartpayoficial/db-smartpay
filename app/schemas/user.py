from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class UserState(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"


class UserBase(BaseModel):
    city_id: UUID
    dni: str
    first_name: str
    middle_name: Optional[str]
    last_name: str
    second_last_name: Optional[str]
    email: str
    prefix: str
    phone: str
    address: str
    state: UserState = UserState.ACTIVE


class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    pass


class UserDB(UserBase):
    user_id: UUID

    class Config:
        orm_mode = True
