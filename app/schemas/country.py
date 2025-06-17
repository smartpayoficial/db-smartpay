from uuid import UUID

from pydantic import BaseModel


class CountryBase(BaseModel):
    name: str
    code: str


class CountryCreate(CountryBase):
    pass


class CountryUpdate(BaseModel):
    # Ajusta los campos según CountryBase, todos opcionales y None por defecto
    # Ejemplo:
    # name: Optional[str] = None
    # code: Optional[str] = None
    pass


class CountryDB(CountryBase):
    country_id: UUID

    class Config:
        orm_mode = True
