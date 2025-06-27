from app.infra.postgres.crud.location import (
    city_crud,
    country_crud,
    location_crud,
    region_crud,
)
from app.services.base import BaseService


class CountryService(BaseService):
    pass


class RegionService(BaseService):
    pass


class CityService(BaseService):
    pass


class LocationService(BaseService):
    pass


country_service = CountryService(crud=country_crud)
region_service = RegionService(crud=region_crud)
city_service = CityService(crud=city_crud)
location_service = LocationService(crud=location_crud)
