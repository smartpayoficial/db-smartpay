from uuid import UUID

from pydantic import BaseModel


class RegionBase(BaseModel):
    name: str
    country_id: UUID


class RegionCreate(RegionBase):
    pass


class RegionUpdate(BaseModel):
    # Ajusta los campos según RegionBase, todos opcionales y None por defecto
    pass


class RegionDB(RegionBase):
    region_id: UUID

    class Config:
        orm_mode = True
