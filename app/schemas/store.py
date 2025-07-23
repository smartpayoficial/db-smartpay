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
    created_at: datetime
    updated_at: datetime
    admin: Optional[UserDB] = None
    country: Optional[CountryDB] = None

    class Config:
        orm_mode = True
        from_attributes = True


class StoreWithCountry(StoreDB):
    class Config:
        orm_mode = True
