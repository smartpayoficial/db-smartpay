from typing import List, Optional, Dict, Any
from uuid import UUID

from app.infra.postgres.crud.base import CRUDBase
from app.infra.postgres.models.store import Store
from app.schemas.store import StoreCreate, StoreUpdate, StoreDB
from typing import Optional
from uuid import UUID
from app.infra.postgres.models.store import Store
from app.schemas.store import StoreDB, StoreContactDB

class CRUDStore(CRUDBase[Store, StoreCreate, StoreUpdate]):
    async def get_with_country(self, *, id: UUID, admin_id: Optional[UUID] = None) -> Optional[StoreDB]:
        """
        Retrieve a single store by its ID with country and contacts.
        """
        query = Store.filter(id=id).prefetch_related("admin", "country", "contacts__account_type")
        if admin_id:
            query = query.filter(admin_id=admin_id)

        store = await query.first()
        if not store:
            return None
        contacts = await store.contacts.all().prefetch_related("account_type")
        store_dict = store.__dict__.copy()
        store_dict["contacts"] = [StoreContactDB.from_orm(c) for c in contacts]

        return StoreDB.parse_obj(store_dict)

    async def get_all_with_country(self, *, skip: int = 0, limit: int = 100, payload: Dict[str, Any] = {}, admin_id: Optional[UUID] = None) -> List[StoreDB]:
        """
        Retrieve all stores with country information.
        """
        query = Store.filter(**payload).prefetch_related(
            'admin', 
            'country', 
            'contacts__account_type'  # ✅ Agregar account_type también
        ).offset(skip).limit(limit)
        
        if admin_id:
            query = query.filter(admin_id=admin_id)
        
        stores = await query
        
        # Convertir contacts de ReverseRelation a lista para cada store
        for store in stores:
            if store.contacts:
                contacts_list = await store.contacts.all()
                store.__dict__['contacts'] = contacts_list
        
        return [StoreDB.from_orm(store) for store in stores]


crud_store = CRUDStore(model=Store)
