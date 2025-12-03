from tortoise import fields
from tortoise.models import Model


class Country(Model):
    country_id = fields.UUIDField(pk=True)
    code = fields.SmallIntField(unique=True)
    name = fields.CharField(max_length=80, unique=True)
    prefix = fields.CharField(max_length=4)

    class Meta:
        table = "country"


class Region(Model):
    region_id = fields.UUIDField(pk=True)
    country = fields.ForeignKeyField("models.Country", related_name="regions")
    name = fields.CharField(max_length=80)

    class Meta:
        table = "region"


class City(Model):
    city_id = fields.UUIDField(pk=True)
    region = fields.ForeignKeyField("models.Region", related_name="cities")
    name = fields.CharField(max_length=80)

    class Meta:
        table = "city"


class Location(Model):
    location_id = fields.UUIDField(pk=True) 
    device = fields.ForeignKeyField(
        "models.Device", 
        related_name="locations",  
        null=True,
        on_delete=fields.RESTRICT
    )
    television = fields.ForeignKeyField(
        "models.Television", 
        related_name="locations", 
        null=True,
        on_delete=fields.RESTRICT
    )
    latitude = fields.FloatField()
    longitude = fields.FloatField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "location"

    def __str__(self):
        return f"Location for device {self.device_id} at {self.created_at}"
