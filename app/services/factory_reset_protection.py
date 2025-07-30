from typing import Optional
from uuid import UUID

from app.infra.postgres.crud.factory_reset_protection import (
    crud_factory_reset_protection,
)
from app.infra.postgres.models.factory_reset_protection import FactoryResetProtection
from app.services.base import BaseService


class FactoryResetProtectionService(BaseService):
    async def get_factory_reset_by_account_id(
        self, id: UUID, store_id: Optional[UUID] = None
    ) -> Optional[FactoryResetProtection]:
        return await self._crud.get_by_account_id(account_id=id, store_id=store_id)


# Instancia global a usar en routers
factory_reset_protection_service = FactoryResetProtectionService(
    crud=crud_factory_reset_protection
)
