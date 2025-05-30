from tortoise import fields
from tortoise.models import Model


class Role(Model):
    role_id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=50)
    description = fields.CharField(max_length=255)

    class Meta:
        table = "role"

    def __str__(self):
        return self.name
