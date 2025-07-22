from tortoise import fields
from tortoise.models import Model


class Store(Model):
    id = fields.UUIDField(pk=True)
    nombre = fields.CharField(max_length=100)
    country = fields.ForeignKeyField("models.Country", related_name="stores")
    admin = fields.ForeignKeyField("models.User", related_name="admin_stores", null=True)
    tokens_disponibles = fields.IntField(default=0)
    plan = fields.CharField(max_length=50)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    back_link = fields.CharField(max_length=255, null=True)
    db_link = fields.CharField(max_length=255, null=True)

    class Meta:
        table = "store"

    def __str__(self):
        return self.nombre
