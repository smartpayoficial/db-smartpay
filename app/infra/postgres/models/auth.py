from enum import Enum

from tortoise import fields
from tortoise.models import Model


class RoleState(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"


class Role(Model):
    role_id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=40, unique=True)
    state = fields.CharEnumField(RoleState, default=RoleState.ACTIVE)

    class Meta:
        table = "role"


class Configuration(Model):
    configuration_id = fields.UUIDField(pk=True)
    tenant_id = fields.UUIDField()
    company_name = fields.CharField(max_length=80)

    class Meta:
        table = "configuration"


class Authentication(Model):
    authentication_id = fields.UUIDField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="authentications")
    role = fields.ForeignKeyField("models.Role", related_name="authentications")
    configuration = fields.ForeignKeyField(
        "models.Configuration", related_name="authentications"
    )
    email = fields.CharField(max_length=80, unique=True)
    password = fields.CharField(max_length=255)

    class Meta:
        table = "authentication"
