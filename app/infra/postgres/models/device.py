from tortoise import fields
from tortoise.models import Model


class Device(Model):
    device_id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=50)
    description = fields.CharField(max_length=255)
    type = fields.CharField(max_length=50)
    status = fields.CharField(max_length=50)

    class Meta:
        table = "device"

    def __str__(self):
        return self.name
