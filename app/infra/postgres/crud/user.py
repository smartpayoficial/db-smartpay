from typing import Any, Optional

from app.infra.postgres.crud.base import CRUDBase
from app.infra.postgres.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_id(self, *, _id: Any) -> Optional[dict]:
        result = (
            await self.model.filter(pk=_id)
            .select_related("role", "city")
            .values(
                "user_id",
                "city_id",
                "city__city_id",
                "city__name",
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
        print("RESULTADO:", result)
        return result[0] if result else None


    async def get_all(
        self,
        *,
        payload: dict = {},
        skip: int = 0,
        limit: int = 10,
    ) -> list[dict]:
        query = self.model.filter(**payload) if payload else self.model.all()
        return (
            await query.select_related("role", "city")
            .offset(skip)
            .limit(limit)
            .values(
                "user_id",
                "city_id",
                "city__city_id",
                "city__name",
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

    async def create(
        self, *, obj_in: UserCreate
    ) -> dict:
        obj_in_data = obj_in.dict()
        model = await self.model.create(**obj_in_data)
        # Cargamos el objeto creado con la relación 'role' y lo convertimos a dict
        result = await self.model.filter(pk=model.pk).select_related("role").values(
            "user_id",
            "city_id",
            "city__city_id",
            "city__name",
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
        return result[0] if result else None

    async def get_by_username(self, username: str) -> Optional[User]:
        return await self.model.filter(username=username).select_related("role").first()


crud_user = CRUDUser(model=User)
