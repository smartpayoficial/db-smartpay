from app.infra.postgres.crud.base import CRUDBase
from app.infra.postgres.models.city import City
from app.schemas.city import CityCreate, CityUpdate


class CRUDCity(CRUDBase[City, CityCreate, CityUpdate]):
    pass


crud_city = CRUDCity(model=City)
