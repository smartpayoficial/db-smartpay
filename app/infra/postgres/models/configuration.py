from tortoise import fields
from tortoise.models import Model


class Configuration(Model):
    configuration_id = fields.UUIDField(pk=True)
    key = fields.CharField(max_length=50, unique=True)
    value = fields.CharField(max_length=255)
    description = fields.CharField(max_length=255)

    class Meta:
        table = "configuration"

    def __str__(self):
        return f"{self.key}: {self.value}"
