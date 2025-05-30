from enum import Enum

from tortoise import fields
from tortoise.models import Model


class GroupState(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"


class Group(Model):
    group_id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=80)
    state = fields.CharEnumField(GroupState, default=GroupState.ACTIVE)

    class Meta:
        table = "group"


class DeviceGroup(Model):
    device_group_id = fields.UUIDField(pk=True)
    device = fields.ForeignKeyField("models.Device", related_name="device_groups")
    group = fields.ForeignKeyField("models.Group", related_name="device_groups")

    class Meta:
        table = "device_group"


class Enrolment(Model):
    enrolment_id = fields.UUIDField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="user_enrolments")
    vendor = fields.ForeignKeyField("models.User", related_name="vendor_enrolments")

    class Meta:
        table = "enrolment"
