from typing import List, Optional, Dict, Any

from app.infra.postgres.crud.base import CRUDBase
from app.infra.postgres.models.store import Store
from app.schemas.store import StoreCreate, StoreUpdate


class CRUDStore(CRUDBase[Store, StoreCreate, StoreUpdate]):
    async def get_with_country(self, *, id: Any) -> Optional[Store]:
        """
        Retrieve a single store by its ID with country information.
        """
        pk = self.model._meta.pk_attr
        return await self.model.filter(**{pk: id}).prefetch_related('country').first()
    
    async def get_all_with_country(self, *, skip: int = 0, limit: int = 100, payload: Dict[str, Any] = {}) -> List[Store]:
        """
        Retrieve all stores with country information.
        """
        return await self.model.filter(**payload).prefetch_related('country').offset(skip).limit(limit).all()


crud_store = CRUDStore(model=Store)
