from uuid import UUID

from pydantic import BaseModel


class CityBase(BaseModel):
    name: str
    region_id: UUID


class CityCreate(CityBase):
    pass


class CityUpdate(CityBase):
    pass


class CityResponse(BaseModel):
    city_id: UUID
    name: str

    class Config:
        orm_mode = True


class CityDB(CityBase):
    city_id: UUID

    class Config:
        orm_mode = True
