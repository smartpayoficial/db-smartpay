from typing import Any, Dict, List, Optional

from tortoise.expressions import Q

from app.infra.postgres.crud.base import CRUDBase
from app.infra.postgres.models import Store, User
from app.schemas.user import UserCreate, UserUpdate
from uuid import UUID

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Obtiene un usuario por ID con todas sus relaciones cargadas."""
        user = await User.filter(user_id=user_id).prefetch_related(
            'role',
            'city__region__country',
            'store__contacts__account_type'
        ).first()

        if user and user.store:
            # Obtener la lista de contacts
            contacts_list = await user.store.contacts.all()

            print(f"Store found: {user.store.nombre}")
            print(f"Number of contacts: {len(contacts_list)}")

            # SOLUCIÓN: Reemplazar el ReverseRelation con la lista real
            # Accedemos directamente al __dict__ del objeto
            user.store.__dict__['contacts'] = contacts_list
            print(f"After replacement - Type: {type(user.store.__dict__['contacts'])}")

        return user

    async def get_all(
        self,
        *,
        filters: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[List[str]] = None,
    ) -> List[User]:
        """
        Obtiene una lista de usuarios con todas las relaciones precargadas.
        """
        query = self.model.all().select_related(
            "role", 
            "city", 
            "city__region", 
            "city__region__country", 
            "store"
        ).prefetch_related(
            "store__contacts__account_type"  # ✅ ESTO FALTABA
        )

        if filters:
            query = query.filter(**filters)

        # Apply ordering
        if order_by:
            query = query.order_by(*order_by)
        elif hasattr(self.model, "created_at"):
            query = query.order_by("-created_at")
        elif hasattr(self.model, "initial_date"):
            query = query.order_by("-initial_date")

        users = await query.offset(skip).limit(limit).all()

        # Forzar la conversión de contacts de ReverseRelation a lista
        for user in users:
            if user.store:
                contacts_list = await user.store.contacts.all()
                user.store.__dict__['contacts'] = contacts_list

        return users

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
        order_by: Optional[List[str]] = None,
    ) -> List[User]:
        """
        Obtiene una lista de usuarios aplicando un filtro Q de Tortoise ORM además de los filtros regulares.
        Las relaciones 'role', 'city', 'city__region', 'city__region__country' y 'store' son precargadas.
        """
        query = self.model.filter(q_filter).select_related("role", "city", "city__region", "city__region__country", "store")
        if payload:
            query = query.filter(**payload)

        # Apply ordering
        if order_by:
            query = query.order_by(*order_by)
        elif hasattr(self.model, "created_at"):
            query = query.order_by("-created_at")
        elif hasattr(self.model, "initial_date"):
            query = query.order_by("-initial_date")

        return await query.offset(skip).limit(limit).all()


crud_user = CRUDUser(model=User)
