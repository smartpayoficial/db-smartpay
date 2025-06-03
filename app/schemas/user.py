from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.infra.postgres.models.user import UserState


class UserBase(BaseModel):
    city_id: UUID
    dni: str
    first_name: str
    middle_name: Optional[str]
    last_name: str
    second_last_name: Optional[str]
    email: EmailStr
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
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
