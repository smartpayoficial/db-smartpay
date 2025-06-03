from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.infra.postgres.models.user import UserState


class UserBase(BaseModel):
    city_id: UUID
    dni: str
    first_name: str
    middle_name: Optional[str]
    last_name: str
    second_last_name: Optional[str]
    email: EmailStr
    prefix: str = Field(
        ...,
        max_length=4,
        min_length=1,
        description="Prefijo telefónico (máximo 4 caracteres)",
    )
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
