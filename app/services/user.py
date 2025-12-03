from typing import Any, Dict, List, Optional

from tortoise.expressions import Q

from app.infra.postgres.crud.user import crud_user
from app.infra.postgres.models.user import User
from app.schemas.user import UserCreate
from app.services.base import BaseService
from uuid import UUID

class UserService(BaseService):
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Obtiene un usuario por ID con relaciones precargadas."""
        return await crud_user.get_by_id(user_id=user_id)
    
    async def get_by_dni(self, *, dni: str) -> Optional[User]:
        return await self.crud.get_by_dni(dni=dni)

    async def get_by_email(self, *, email: str) -> Optional[User]:
        return await self.crud.get_by_email(email=email)
        
    async def get_all_with_filter(self, q_filter: Q, *, payload: Dict[str, Any] = None, skip: int = 0, limit: int = 100) -> List[User]:
        """Obtiene usuarios aplicando un filtro Q de Tortoise ORM además de los filtros regulares."""
        return await self.crud.get_all_with_filter(q_filter=q_filter, payload=payload, skip=skip, limit=limit)

    async def create(self, *, obj_in: UserCreate) -> Optional[User]:
        """Crea un usuario y precarga las relaciones para la respuesta."""
        # Primero, crea el usuario usando el método base
        new_user = await super().create(obj_in=obj_in)
        
        # Si el usuario se creó correctamente, obténlo de nuevo con las relaciones
        if new_user:
            return await self.get_by_id(user_id=new_user.user_id)
        
        return None


user_service = UserService(crud=crud_user)
