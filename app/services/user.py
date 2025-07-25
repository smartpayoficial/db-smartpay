from typing import Any, Dict, List, Optional

from tortoise.expressions import Q

from app.infra.postgres.crud.user import crud_user
from app.infra.postgres.models.user import User
from app.services.base import BaseService


class UserService(BaseService):
    async def get_by_dni(self, *, dni: str) -> Optional[User]:
        return await self.crud.get_by_dni(dni=dni)

    async def get_by_email(self, *, email: str) -> Optional[User]:
        return await self.crud.get_by_email(email=email)
        
    async def get_all_with_filter(self, q_filter: Q, *, payload: Dict[str, Any] = None, skip: int = 0, limit: int = 100) -> List[User]:
        """Obtiene usuarios aplicando un filtro Q de Tortoise ORM además de los filtros regulares."""
        return await self.crud.get_all_with_filter(q_filter=q_filter, payload=payload, skip=skip, limit=limit)


user_service = UserService(crud=crud_user)
