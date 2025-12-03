from tortoise import fields
from tortoise.models import Model


class Country(Model):
    country_id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=100)
    code = fields.CharField(max_length=3)
    phone_code = fields.CharField(max_length=10)
    flag_icon_url = fields.CharField(max_length=255)

    class Meta:
        table = "country"

    def __str__(self):
        return self.name
