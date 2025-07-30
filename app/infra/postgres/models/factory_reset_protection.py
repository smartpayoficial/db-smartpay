from enum import Enum

from tortoise import fields
from tortoise.models import Model

from app.infra.postgres.models.store import Store


class FactoryResetProtectionState(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"


class FactoryResetProtection(Model):
    factory_reset_protection_id = fields.UUIDField(pk=True)
    account_id = fields.CharField(max_length=40, index=True)
    name = fields.CharField(max_length=255)
    email = fields.CharField(max_length=80, index=True)
    state = fields.CharEnumField(
        FactoryResetProtectionState, default=FactoryResetProtectionState.ACTIVE
    )
    store = fields.ForeignKeyField('models.Store', related_name='factory_reset_protections', null=True)
    
    class Meta:
        table = "factoryResetProtection"
        unique_together = (("account_id", "store"), ("email", "store"))

    def __str__(self):
        return f"{self.account_id}: {self.email}"
