from enum import Enum

from tortoise import fields
from tortoise.models import Model


class FactoryResetProtectionState(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"


class FactoryResetProtection(Model):
    factory_reset_protection_id = fields.UUIDField(pk=True)
    account_id = fields.CharField(max_length=40, unique=True)
    name = fields.CharField(max_length=255)
    email = fields.CharField(max_length=80)
    state = fields.CharEnumField(
        FactoryResetProtectionState, default=FactoryResetProtectionState.ACTIVE
    )

    class Meta:
        table = "factoryResetProtection"

    def __str__(self):
        return f"{self.key}: {self.value}"
