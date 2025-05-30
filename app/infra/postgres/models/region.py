from tortoise import fields
from tortoise.models import Model


class Region(Model):
    region_id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=100)
    country = fields.ForeignKeyField("models.Country", related_name="regions")

    class Meta:
        table = "region"

    def __str__(self):
        return self.name
