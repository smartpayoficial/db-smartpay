from uuid import UUID

from typing import Optional
from pydantic import BaseModel


class CountryBase(BaseModel):
    name: str
    code: str
    phone_code: Optional[str] = None
    flag_icon_url: Optional[str] = None


class CountryCreate(CountryBase):
    pass


class CountryUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    phone_code: Optional[str] = None
    flag_icon_url: Optional[str] = None


class CountryDB(CountryBase):
    country_id: UUID

    class Config:
        orm_mode = True
