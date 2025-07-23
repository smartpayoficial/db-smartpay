from typing import List, Optional, Dict, Any
from uuid import UUID

from app.infra.postgres.crud.base import CRUDBase
from app.infra.postgres.models.store import Store
from app.schemas.store import StoreCreate, StoreUpdate, StoreDB


class CRUDStore(CRUDBase[Store, StoreCreate, StoreUpdate]):
    async def get_with_country(self, *, id: UUID, admin_id: Optional[UUID] = None) -> Optional[StoreDB]:
        """
        Retrieve a single store by its ID with country information.
        """
        query = Store.filter(id=id).prefetch_related("admin", "country")
        if admin_id:
            query = query.filter(admin_id=admin_id)
        store = await query.first()
        return StoreDB.from_orm(store) if store else None

    async def get_all_with_country(self, *, skip: int = 0, limit: int = 100, payload: Dict[str, Any] = {}, admin_id: Optional[UUID] = None) -> List[StoreDB]:
        """
        Retrieve all stores with country information.
        """
        query = Store.filter(**payload).prefetch_related('admin', 'country').offset(skip).limit(limit)
        if admin_id:
            query = query.filter(admin_id=admin_id)
        stores = await query
        return [StoreDB.from_orm(store) for store in stores]


crud_store = CRUDStore(model=Store)
