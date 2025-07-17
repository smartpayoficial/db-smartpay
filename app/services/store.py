from typing import List, Optional, Dict, Any
from uuid import UUID

from app.infra.postgres.crud.store import crud_store
from app.infra.postgres.models.store import Store
from app.services.base import BaseService


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


store_service = StoreService(crud=crud_store)
