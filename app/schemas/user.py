from datetime import datetime
from typing import Optional, Dict, Any, Union
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.infra.postgres.models.user import UserState
from app.schemas.role import RoleOut


class UserBase(BaseModel):
    city_id: UUID
    store_id: Optional[UUID] = None
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
    username: str
    password: str
    role_id: UUID
    state: UserState = UserState.ACTIVE


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    city_id: Optional[UUID] = None
    store_id: Optional[UUID] = None
    dni: Optional[str] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    second_last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    prefix: Optional[str] = Field(
        None,
        max_length=4,
        min_length=1,
        description="Prefijo telefónico (máximo 4 caracteres)",
    )
    phone: Optional[str] = None
    address: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    role_id: Optional[UUID] = None
    state: Optional[UserState] = None


class UserDB(UserBase):
    user_id: UUID
    role: Optional[Union[RoleOut, Dict[str, Any]]] = None  # Acepta RoleOut o dict
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True
        json_encoders = {
            UUID: str
        }


class UserPaymentResponse(BaseModel):
    first_name: str
    middle_name: Optional[str]
    last_name: str
    second_last_name: Optional[str]

    class Config:
        orm_mode = True
