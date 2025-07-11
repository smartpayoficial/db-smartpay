from typing import Optional

from app.infra.postgres.crud.user import crud_user
from app.infra.postgres.models.user import User
from app.services.base import BaseService


class UserService(BaseService):
    async def get_by_dni(self, *, dni: str) -> Optional[User]:
        return await self.crud.get_by_dni(dni=dni)

    async def get_by_email(self, *, email: str) -> Optional[User]:
        return await self.crud.get_by_email(email=email)


user_service = UserService(crud=crud_user)
