from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


class CountryOut(BaseModel):
    country_id: UUID
    name: str
    code: str

    class Config:
        orm_mode = True


class RegionOut(BaseModel):
    region_id: UUID
    name: str
    country: CountryOut

    class Config:
        orm_mode = True


class CityOut(BaseModel):
    city_id: UUID
    name: str
    region: RegionOut

    class Config:
        orm_mode = True


class RoleOut(BaseModel):
    role_id: UUID
    name: str
    description: Optional[str]

    class Config:
        orm_mode = True


class StoreOut(BaseModel):
    id: UUID
    nombre: str

    class Config:
        orm_mode = True


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
