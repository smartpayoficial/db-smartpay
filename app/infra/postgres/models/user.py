from enum import Enum

from tortoise import fields
from tortoise.models import Model


class UserState(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"


class User(Model):
    user_id = fields.UUIDField(pk=True)
    city = fields.ForeignKeyField("models.City", related_name="users")
    dni = fields.CharField(max_length=16, unique=True)
    first_name = fields.CharField(max_length=40)
    middle_name = fields.CharField(max_length=40, null=True)
    last_name = fields.CharField(max_length=40)
    second_last_name = fields.CharField(max_length=40, null=True)
    email = fields.CharField(max_length=80)
    prefix = fields.CharField(max_length=4)
    phone = fields.CharField(max_length=15)
    address = fields.CharField(max_length=255)
    state = fields.CharEnumField(UserState, default=UserState.ACTIVE)

    class Meta:
        table = "user"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
