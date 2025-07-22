from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from app.schemas.country import CountryDB
from app.schemas.user import UserDB


class StoreBase(BaseModel):
    nombre: str
    country_id: UUID
    admin_id: Optional[UUID] = None
    tokens_disponibles: int = 0
    plan: str
    back_link: Optional[str] = None
    db_link: Optional[str] = None


class StoreCreate(StoreBase):
    pass


class StoreUpdate(BaseModel):
    nombre: Optional[str] = None
    country_id: Optional[UUID] = None
    admin_id: Optional[UUID] = None
    tokens_disponibles: Optional[int] = None
    plan: Optional[str] = None
    back_link: Optional[str] = None
    db_link: Optional[str] = None


class StoreDB(StoreBase):
    id: UUID
    admin: Optional[UserDB] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class StoreWithCountry(StoreDB):
    country: Optional[CountryDB] = None

    class Config:
        orm_mode = True
