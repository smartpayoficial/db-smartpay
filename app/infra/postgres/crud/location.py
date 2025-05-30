from app.infra.postgres.crud.base import CRUDBase
from app.infra.postgres.models.location import City, Country, Region
from app.schemas.location import (
    CityCreate,
    CityUpdate,
    CountryCreate,
    CountryUpdate,
    RegionCreate,
    RegionUpdate,
)


class CRUDCountry(CRUDBase[Country, CountryCreate, CountryUpdate]):
    pass


class CRUDRegion(CRUDBase[Region, RegionCreate, RegionUpdate]):
    pass


class CRUDCity(CRUDBase[City, CityCreate, CityUpdate]):
    pass


country_crud = CRUDCountry(model=Country)
region_crud = CRUDRegion(model=Region)
city_crud = CRUDCity(model=City)
