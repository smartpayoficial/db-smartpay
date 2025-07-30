from tortoise import fields
from tortoise.models import Model


class Configuration(Model):
    configuration_id = fields.UUIDField(pk=True)
    key = fields.CharField(max_length=50)  # No longer unique by itself
    value = fields.CharField(max_length=1000)  # Increased from 255 to 1000 characters
    description = fields.CharField(max_length=255)
    store_id = fields.UUIDField(null=True)  # Added via migration

    class Meta:
        table = "configuration"
        unique_together = (("key", "store_id"),)  # Composite unique constraint

    def __str__(self):
        return f"{self.key}: {self.value}"
