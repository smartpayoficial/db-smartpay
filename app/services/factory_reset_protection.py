from app.infra.postgres.crud.factory_reset_protection import (
    crud_factory_reset_protection,
)
from app.services.base import BaseService


class FactoryResetProtectionService(BaseService):
    pass


factory_reset_protection_service = FactoryResetProtectionService(
    crud=crud_factory_reset_protection
)
