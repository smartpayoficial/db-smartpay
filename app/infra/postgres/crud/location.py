from typing import List, Optional

from app.infra.postgres.crud.base import CRUDBase
from app.infra.postgres.models.location import City, Country, Location, Region
from app.schemas.location import (
    CityCreate,
    CityUpdate,
    CountryCreate,
    CountryUpdate,
    LocationCreate,
    LocationUpdate,
    RegionCreate,
    RegionUpdate,
)


class CRUDCountry(CRUDBase[Country, CountryCreate, CountryUpdate]):
    pass


class CRUDRegion(CRUDBase[Region, RegionCreate, RegionUpdate]):
    pass


class CRUDCity(CRUDBase[City, CityCreate, CityUpdate]):
    pass


class CRUDLocation(CRUDBase[Location, LocationCreate, LocationUpdate]):
    async def get_all(
        self, payload: Optional[dict], skip: int = 0, limit: int = 100
    ) -> List[dict]:
        query = self.model.all()
        if payload:
            query = query.filter(**payload)

        # Order by most recent
        query = query.order_by("-created_at")

        return await query.offset(skip).limit(limit).values()

    async def get_last_by_device_id(self, device_id: int) -> Optional[Location]:
        location = (
            await Location.filter(device_id=device_id).order_by("-created_at").first()
        )
        if location:
            return location
        return None


country_crud = CRUDCountry(model=Country)
region_crud = CRUDRegion(model=Region)
city_crud = CRUDCity(model=City)
location_crud = CRUDLocation(model=Location)
