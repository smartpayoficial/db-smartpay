from typing import List, Optional
from uuid import UUID

from app.infra.postgres.crud.base import CRUDBase
from app.infra.postgres.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    # Sobreescribir get_by_id para cargar la relación 'role'
    async def get_by_id(self, _id: UUID) -> Optional[User]:
        # Usamos .select_related('role') para cargar la relación 'role'
        return await self.model.filter(pk=_id).select_related("role").first()

    # Sobreescribir get_all para cargar la relación 'role'
    async def get_all(
        self,
        *,
        payload: dict = {},
        skip: int = 0,
        limit: int = 10,
    ) -> List[
        User
    ]:  # El tipo de retorno ahora es una lista de instancias de modelo User
        query = self.model.filter(**payload) if payload else self.model
        # Usamos .select_related('role') para cargar la relación 'role'
        # ¡IMPORTANTE!: No usar .values() aquí, ya que queremos el objeto ORM
        return await query.select_related("role").offset(skip).limit(limit)

    # Sobreescribir create para cargar la relación 'role' al devolver el objeto creado
    async def create(
        self, *, obj_in: UserCreate
    ) -> User:  # El tipo de retorno ahora es una instancia de modelo User
        obj_in_data = obj_in.dict()
        model = await self.model.create(**obj_in_data)
        # Cargamos el objeto creado con la relación 'role'
        return await self.model.filter(pk=model.pk).select_related("role").first()

    async def get_by_username(self, username: str) -> Optional[User]:
        return await self.model.filter(username=username).select_related("role").first()


crud_user = CRUDUser(model=User)
