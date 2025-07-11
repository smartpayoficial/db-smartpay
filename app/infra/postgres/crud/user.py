from typing import Any, Dict, List, Optional

from app.infra.postgres.crud.base import CRUDBase
from app.infra.postgres.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get(self, *, id: Any) -> Optional[User]:
        """
        Obtiene un usuario por su ID, con las relaciones 'role' y 'city' precargadas.
        """
        return await self.model.filter(pk=id).select_related("role", "city").first()

    async def get_all(
        self,
        *,
        filters: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[User]:
        """
        Obtiene una lista de usuarios, con las relaciones 'role' y 'city' precargadas.
        """
        query = self.model.all().select_related("role", "city")
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
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        
        await db_obj.save()
        return db_obj
        
    async def get_by_dni(self, *, dni: str) -> Optional[User]:
        """
        Obtiene un usuario por su DNI, con las relaciones 'role' y 'city' precargadas.
        """
        return await self.model.filter(dni=dni).select_related("role", "city").first()
        
    async def get_by_email(self, *, email: str) -> Optional[User]:
        """
        Obtiene un usuario por su email, con las relaciones 'role' y 'city' precargadas.
        """
        return await self.model.filter(email__iexact=email).select_related("role", "city").first()


crud_user = CRUDUser(model=User)
