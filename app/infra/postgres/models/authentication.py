from tortoise import fields
from tortoise.models import Model


class Authentication(Model):
    authentication_id = fields.UUIDField(pk=True)
    username = fields.CharField(max_length=50, unique=True)
    password = fields.CharField(max_length=255)
    email = fields.CharField(max_length=255, unique=True)

    class Meta:
        table = "authentication"

    def __str__(self):
        return self.username
