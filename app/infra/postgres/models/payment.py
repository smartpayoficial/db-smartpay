from enum import Enum

from tortoise import fields
from tortoise.models import Model


class PaymentState(str, Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    FAILED = "Failed"
    RETURNED = "Returned"


class Plan(Model):
    plan_id = fields.UUIDField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="user_plans")
    vendor = fields.ForeignKeyField("models.User", related_name="vendor_plans")
    device = fields.ForeignKeyField("models.Device", related_name="plans")
    initial_date = fields.DateField()
    quotas = fields.SmallIntField()
    contract = fields.CharField(max_length=80)

    class Meta:
        table = "plan"


class Payment(Model):
    payment_id = fields.UUIDField(pk=True)
    device = fields.ForeignKeyField("models.Device", related_name="payments")
    plan = fields.ForeignKeyField("models.Plan", related_name="payments")
    value = fields.DecimalField(max_digits=10, decimal_places=2)
    method = fields.CharField(max_length=20)
    state = fields.CharEnumField(PaymentState)
    date = fields.DatetimeField()
    reference = fields.CharField(max_length=80)

    class Meta:
        table = "payment"
