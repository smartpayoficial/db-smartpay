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
    pass


crud_factory_reset_protection = CRUDFactoryResetProtection(model=FactoryResetProtection)
