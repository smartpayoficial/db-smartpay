from tortoise import fields
from tortoise.models import Model


class Country(Model):
    country_id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=100)
    code = fields.CharField(max_length=3)

    class Meta:
        table = "country"

    def __str__(self):
        return self.name
