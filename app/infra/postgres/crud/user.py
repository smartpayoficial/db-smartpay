from typing import Any, Dict, List, Optional

from tortoise.expressions import Q

from app.infra.postgres.crud.base import CRUDBase
from app.infra.postgres.models import Store, User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get(self, *, id: Any) -> Optional[User]:
        """
        Obtiene un usuario por su ID, con las relaciones 'role', 'city', 'city__region', 'city__region__country' y 'store' precargadas.
        """
        return await self.model.filter(pk=id).select_related("role", "city", "city__region", "city__region__country", "store").first()

    async def get_all(
        self,
        *,
        filters: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[User]:
        """
        Obtiene una lista de usuarios, con las relaciones 'role', 'city', 'city__region', 'city__region__country' y 'store' precargadas.
        """
        query = self.model.all().select_related("role", "city", "city__region", "city__region__country", "store")
        if filters:
            query = query.filter(**filters)
        return await query.offset(skip).limit(limit)

    async def create(self, *, obj_in: UserCreate) -> User:
        """
        Crea un nuevo usuario y devuelve la instancia con las relaciones precargadas.
        """
        created_user = await super().create(obj_in=obj_in)
        # Re-obtenemos el usuario para cargar las relaciones
        return await self.get(id=created_user.pk)

    async def update(self, *, id: Any, obj_in: UserUpdate) -> Optional[User]:
        """
        Actualiza un usuario y devuelve la instancia con las relaciones precargadas.
        """
        # El método update de la base no devuelve el objeto, así que no usamos super()
        db_obj = await self.get(id=id)
        if not db_obj:
            return None
        
        obj_data = obj_in.dict(exclude_unset=True)

        # Handle store assignment separately
        if "store_id" in obj_data:
            store_id = obj_data.pop("store_id")
            if store_id:
                store_obj = await Store.get_or_none(id=store_id)
                db_obj.store = store_obj
            else:
                db_obj.store = None

        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        
        await db_obj.save()
        return db_obj
        
    async def get_by_dni(self, *, dni: str) -> Optional[User]:
        """
        Obtiene un usuario por su DNI, con las relaciones 'role', 'city', 'city__region', 'city__region__country' y 'store' precargadas.
        """
        return await self.model.filter(dni=dni).select_related("role", "city", "city__region", "city__region__country", "store").first()
        
    async def get_by_email(self, *, email: str) -> Optional[User]:
        """
        Obtiene un usuario por su email, con las relaciones 'role', 'city', 'city__region', 'city__region__country' y 'store' precargadas.
        """
        return await self.model.filter(email__iexact=email).select_related("role", "city", "city__region", "city__region__country", "store").first()
        
    async def get_all_with_filter(
        self,
        *,
        q_filter: Q,
        payload: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[User]:
        """
        Obtiene una lista de usuarios aplicando un filtro Q de Tortoise ORM además de los filtros regulares.
        Las relaciones 'role', 'city', 'city__region', 'city__region__country' y 'store' son precargadas.
        """
        query = self.model.filter(q_filter).select_related("role", "city", "city__region", "city__region__country", "store")
        if payload:
            query = query.filter(**payload)
        return await query.offset(skip).limit(limit)


crud_user = CRUDUser(model=User)
