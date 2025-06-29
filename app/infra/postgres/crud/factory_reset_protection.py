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
        self, account_id: UUID
    ) -> Optional[FactoryResetProtection]:
        return await self.model.filter(account_id=account_id).first()


# Instancia que se importa en el servicio
crud_factory_reset_protection = CRUDFactoryResetProtection(model=FactoryResetProtection)
