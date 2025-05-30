from app.infra.postgres.crud.base import CRUDBase
from app.infra.postgres.models.country import Country
from app.schemas.country import CountryCreate, CountryUpdate


class CRUDCountry(CRUDBase[Country, CountryCreate, CountryUpdate]):
    pass


crud_country = CRUDCountry(model=Country)
