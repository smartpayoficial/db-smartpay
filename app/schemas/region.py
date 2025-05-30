from uuid import UUID

from pydantic import BaseModel


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
