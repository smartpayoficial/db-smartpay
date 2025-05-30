from app.infra.postgres.crud.country import crud_country
from app.services.base import BaseService


class CountryService(BaseService):
    pass


country_service = CountryService(crud=crud_country)
