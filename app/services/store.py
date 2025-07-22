from typing import List, Optional, Dict, Any
from uuid import UUID

from app.infra.postgres.crud.store import crud_store
from app.infra.postgres.models.store import Store
from app.services.base import BaseService
from app.schemas.store import StoreCreate, StoreUpdate


class StoreService(BaseService):
    async def get_with_country(self, *, id: UUID) -> Optional[Store]:
        """
        Retrieve a single store by its ID with country information.
        """
        return await self.crud.get_with_country(id=id)
    
    async def get_all_with_country(self, *, skip: int = 0, limit: int = 100, payload: Dict[str, Any] = {}) -> List[Store]:
        """
        Retrieve all stores with country information.
        """
        return await self.crud.get_all_with_country(skip=skip, limit=limit, payload=payload)

    async def create(self, *, obj_in: StoreCreate) -> Store:
        store_data = obj_in.dict()
        if 'admin_id' in store_data and store_data['admin_id'] is None:
            del store_data['admin_id']
        return await self.crud.create(obj_in=store_data)

    async def update(self, *, id: UUID, obj_in: StoreUpdate) -> Store:
        update_data = obj_in.dict(exclude_unset=True)
        if 'admin_id' in update_data and update_data['admin_id'] is None:
            del update_data['admin_id']
        return await self.crud.update(id=id, obj_in=update_data)


store_service = StoreService(crud=crud_store)
