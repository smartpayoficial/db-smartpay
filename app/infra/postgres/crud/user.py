from typing import Any, Optional

from app.infra.postgres.crud.base import CRUDBase
from app.infra.postgres.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    # Sobreescribir get_by_id para cargar la relación 'role' y devolver un dict
    async def get_by_id(self, *, _id: Any) -> Optional[dict]:
        result = (
            await self.model.filter(pk=_id)
            .select_related("role")
            .values(
                "user_id",
                "city_id",
                "dni",
                "first_name",
                "middle_name",
                "last_name",
                "second_last_name",
                "email",
                "prefix",
                "phone",
                "address",
                "username",
                "state",
                "created_at",
                "updated_at",
                "role_id",
                "role__role_id",
                "role__name",
                "role__description",
            )
        )
        return result[0] if result else None

    # Sobreescribir get_all para cargar la relación 'role' y devolver lista de dicts
    async def get_all(
        self,
        *,
        payload: dict = {},
        skip: int = 0,
        limit: int = 10,
    ) -> list[dict]:
        query = self.model.filter(**payload) if payload else self.model.all()
        return (
            await query.select_related("role")
            .offset(skip)
            .limit(limit)
            .values(
                "user_id",
                "city_id",
                "dni",
                "first_name",
                "middle_name",
                "last_name",
                "second_last_name",
                "email",
                "prefix",
                "phone",
                "address",
                "username",
                "state",
                "created_at",
                "updated_at",
                "role_id",
                "role__role_id",
                "role__name",
                "role__description",
            )
        )

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
