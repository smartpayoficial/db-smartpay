from enum import Enum

from tortoise import fields
from tortoise.models import Model


class TelevisionState(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"

class Television(Model):
    television_id = fields.UUIDField(pk=True)
    enrolment = fields.OneToOneField("models.Enrolment", related_name="television")
    brand = fields.CharField(max_length=50)
    model = fields.CharField(max_length=100)
    android_version = fields.IntField(null=True)
    serial_number = fields.CharField(max_length=100, unique=True)
    board = fields.CharField(max_length=50)
    fingerprint = fields.CharField(max_length=500)
    state = fields.CharEnumField(TelevisionState, default=TelevisionState.ACTIVE)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "television"

    def __str__(self):
        return self.name
