from uuid import UUID

from pydantic import BaseModel


class CountryBase(BaseModel):
    name: str
    code: str


class CountryCreate(CountryBase):
    pass


class CountryUpdate(CountryBase):
    pass


class CountryDB(CountryBase):
    country_id: UUID

    class Config:
        orm_mode = True
