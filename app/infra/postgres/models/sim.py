from tortoise import fields
from tortoise.models import Model


class Sim(Model):
    sim_id = fields.UUIDField(pk=True)
    device = fields.ForeignKeyField("models.Device", related_name="sims")
    icc_id = fields.CharField(max_length=30, unique=True)
    slot_index = fields.CharField(max_length=10)
    operator = fields.CharField(max_length=50)
    number = fields.CharField(max_length=20, unique=True)
    state = fields.CharField(max_length=20, default="Active")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "sim"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.number} ({self.operator})"
