from app.infra.postgres.crud.city import crud_city
from app.services.base import BaseService


class CityService(BaseService):
    pass


city_service = CityService(crud=crud_city)
