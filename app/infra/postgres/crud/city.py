from typing import Any, Optional

from app.infra.postgres.crud.base import CRUDBase
from app.infra.postgres.models.city import City
from app.schemas.city import CityCreate, CityUpdate


class CRUDCity(CRUDBase[City, CityCreate, CityUpdate]):
    async def get(self, *, id: Any) -> Optional[City]:
        return await self.model.filter(pk=id).first()


crud_city = CRUDCity(model=City)
