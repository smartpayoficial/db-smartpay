from tortoise import fields
from tortoise.models import Model


class Enrolment(Model):
    enrolment_id = fields.UUIDField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="enrolments")
    vendor = fields.ForeignKeyField("models.User", related_name="vendor_enrolments")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "enrolment"

    def __str__(self):
        return f"Enrolment {self.enrolment_id}"
