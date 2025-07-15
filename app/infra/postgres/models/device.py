from enum import Enum

from tortoise import fields
from tortoise.models import Model


class DeviceState(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"


class Device(Model):
    device_id = fields.UUIDField(pk=True)
    enrolment = fields.OneToOneField("models.Enrolment", related_name="device")
    name = fields.CharField(max_length=80)
    imei = fields.CharField(max_length=15, unique=True)
    imei_two = fields.CharField(max_length=15)
    serial_number = fields.CharField(max_length=20)
    model = fields.CharField(max_length=40)
    brand = fields.CharField(max_length=40)
    product_name = fields.CharField(max_length=40)
    state = fields.CharEnumField(DeviceState, default=DeviceState.ACTIVE)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "device"

    def __str__(self):
        return self.name
