from typing import Optional
from uuid import UUID

from app.infra.postgres.crud.base import CRUDBase
from app.infra.postgres.models.factory_reset_protection import FactoryResetProtection
from app.schemas.factory_reset_protection import (
    FactoryResetProtectionCreate,
    FactoryResetProtectionUpdate,
)


class CRUDFactoryResetProtection(
    CRUDBase[
        FactoryResetProtection,
        FactoryResetProtectionCreate,
        FactoryResetProtectionUpdate,
    ]
):
    async def get_by_account_id(
        self, account_id: UUID, store_id: Optional[UUID] = None
    ) -> Optional[FactoryResetProtection]:
        filters = {"account_id": account_id}
        if store_id:
            filters["store_id"] = store_id
        return await self.model.filter(**filters).first()


# Instancia que se importa en el servicio
crud_factory_reset_protection = CRUDFactoryResetProtection(model=FactoryResetProtection)
