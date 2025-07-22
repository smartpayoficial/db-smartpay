from typing import List, Optional, Dict, Any
from uuid import UUID

from app.infra.postgres.crud.base import CRUDBase
from app.infra.postgres.models.store import Store
from app.schemas.store import StoreCreate, StoreUpdate


class CRUDStore(CRUDBase[Store, StoreCreate, StoreUpdate]):
    async def get_with_country(self, *, id: UUID) -> Optional[Dict[str, Any]]:
        """
        Retrieve a single store by its ID with country information.
        """
        store = await Store.filter(id=id).prefetch_related(
            "country", "admin", "admin__role"
        ).first()
        if not store:
            return None
        return await self._store_to_dict(store)

    async def _store_to_dict(self, store: Store) -> Dict[str, Any]:
        return {
            "id": str(store.id),
            "nombre": store.nombre,
            "country": await self._country_to_dict(store.country),
            "admin": await self._user_to_dict(store.admin) if store.admin else None,
            "tokens_disponibles": store.tokens_disponibles,
            "plan": store.plan,
            "back_link": store.back_link,
            "db_link": store.db_link,
            "created_at": store.created_at.isoformat(),
            "updated_at": store.updated_at.isoformat()
        }

    async def get_all_with_country(self, *, skip: int = 0, limit: int = 100, payload: Dict[str, Any] = {}) -> List[Store]:
        """
        Retrieve all stores with country information.
        """
        return await self.model.filter(**payload).prefetch_related('country').offset(skip).limit(limit).all()


crud_store = CRUDStore(model=Store)
