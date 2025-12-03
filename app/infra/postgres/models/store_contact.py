import uuid
from tortoise import fields
from app.infra.postgres.models.base import TimestampedModel

class StoreContact(TimestampedModel):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    store = fields.ForeignKeyField("models.Store", related_name="contacts")
    account_type = fields.ForeignKeyField("models.AccountType", related_name="store_contacts")
    contact_details = fields.JSONField()
    description = fields.CharField(max_length=100, null=True)

    class Meta:
        table = "store_contact"

    def __str__(self):
        return f"{self.store} - {self.account_type}"