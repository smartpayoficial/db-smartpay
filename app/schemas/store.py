from datetime import datetime
from typing import List, Optional
from uuid import UUID

from app.schemas.store_contact import StoreContactDB
from pydantic import BaseModel, validator
from app.schemas.country import CountryDB
from app.schemas.user import UserDB
from typing import List 

from tortoise.fields.relational import ReverseRelation

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
    contacts: List[StoreContactDB] = []
    
    @validator('contacts', pre=True, always=True)
    def resolve_contacts(cls, v):
        """Convierte ReverseRelation a lista."""
        if v is None:
            return []
        if isinstance(v, ReverseRelation):
            if hasattr(v, '_fetched') and v._fetched is not None:
                return list(v._fetched) if not isinstance(v._fetched, bool) else []
            return []
        if isinstance(v, list):
            return v
        return []
    class Config:
        orm_mode = True
        from_attributes = True


class StoreWithCountry(StoreDB):
    class Config:
        orm_mode = True
