from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, validator
from tortoise.fields.relational import ReverseRelation

from app.schemas.store_contact import StoreContactDB


class CountryOut(BaseModel):
    country_id: UUID
    name: str
    code: str

    class Config:
        orm_mode = True
        from_attributes = True


class RegionOut(BaseModel):
    region_id: UUID
    name: str
    country: CountryOut

    class Config:
        orm_mode = True
        from_attributes = True


class CityOut(BaseModel):
    city_id: UUID
    name: str
    region: RegionOut

    class Config:
        orm_mode = True
        from_attributes = True


class RoleOut(BaseModel):
    role_id: UUID
    name: str
    description: Optional[str]

    class Config:
        orm_mode = True
        from_attributes = True


class StoreOut(BaseModel):
    id: UUID
    nombre: str
    tokens_disponibles: Optional[int] = None
    country_id: Optional[UUID] = None
    contacts: List[StoreContactDB] = []

    @validator('contacts', pre=True, always=True)
    def resolve_contacts(cls, v):
        """Convierte ReverseRelation a lista."""
        print(f"DEBUG contacts validator - Type: {type(v)}, Value: {v}")
        
        # Si es None, retornar lista vacía
        if v is None:
            return []
        
        # Si es ReverseRelation, necesitamos obtener los objetos relacionados
        if isinstance(v, ReverseRelation):
            # Acceder al QuerySet interno
            if hasattr(v, 'related_objects'):
                result = list(v.related_objects)
                print(f"DEBUG: Found {len(result)} items in related_objects")
                return result
            
            # Otra opción: intentar iterar directamente
            try:
                # El ReverseRelation puede ser iterable si fue precargado
                result = list(v)
                print(f"DEBUG: Converted to list with {len(result)} items")
                return result
            except Exception as e:
                print(f"DEBUG: Could not iterate ReverseRelation: {e}")
                return []
        
        # Si ya es una lista, retornarla
        if isinstance(v, list):
            print(f"DEBUG: Already a list with {len(v)} items")
            return v
        
        # Fallback
        print(f"DEBUG: Unexpected type {type(v)}, returning empty list")
        return []

    class Config:
        orm_mode = True
        from_attributes = True


class UserOut(BaseModel):
    user_id: UUID
    dni: str
    first_name: str
    middle_name: Optional[str]
    last_name: str
    second_last_name: Optional[str]
    email: EmailStr
    prefix: str
    phone: str
    address: str
    username: str
    state: str
    created_at: datetime
    updated_at: datetime
    role: RoleOut
    city: Optional[CityOut]
    store: Optional[StoreOut]

    class Config:
        orm_mode = True
        from_attributes = True