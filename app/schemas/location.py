from uuid import UUID

from pydantic import BaseModel


class CountryBase(BaseModel):
    code: int
    name: str
    prefix: str


class CountryCreate(CountryBase):
    pass


class CountryUpdate(CountryBase):
    pass


class CountryDB(CountryBase):
    country_id: UUID

    class Config:
        orm_mode = True


class RegionBase(BaseModel):
    name: str
    country_id: UUID


class RegionCreate(RegionBase):
    pass


class RegionUpdate(RegionBase):
    pass


class RegionDB(RegionBase):
    region_id: UUID

    class Config:
        orm_mode = True


class CityBase(BaseModel):
    name: str
    region_id: UUID


class CityCreate(CityBase):
    pass


class CityUpdate(CityBase):
    pass


from datetime import datetime
from typing import Optional

class CityDB(CityBase):
    city_id: UUID

    class Config:
        orm_mode = True


class LocationBase(BaseModel):
    device_id: UUID
    latitude: float
    longitude: float


class LocationCreate(LocationBase):
    pass


class LocationUpdate(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class LocationDB(LocationBase):
    location_id: UUID
    created_at: datetime

    class Config:
        orm_mode = True
