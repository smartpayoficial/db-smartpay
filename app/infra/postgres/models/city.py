from tortoise import fields
from tortoise.models import Model


class City(Model):
    city_id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=100)
    region = fields.ForeignKeyField("models.Region", related_name="cities")

    class Meta:
        table = "city"

    def __str__(self):
        return self.name
