from tortoise import fields
from enum import Enum
from app.infra.postgres.models.base import TimestampedModel

# Define the Enum for the category. This must be consistent with the DB migration.
class AccountCategoryEnum(str, Enum):
    CONTACT = "CONTACT"
    BANK_ACCOUNT = "BANK_ACCOUNT"
    MOBILE_PAYMENT = "MOBILE_PAYMENT"
    PAYMENT_GATEWAY = "PAYMENT_GATEWAY"
    PUBLIC_PROFILE = "PUBLIC_PROFILE"
    WEBHOOK = "WEBHOOK"
    LOCATION = "LOCATION"

class AccountType(TimestampedModel):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True)
    description = fields.TextField(null=True)
    icon_url = fields.CharField(max_length=255, null=True)
    is_international = fields.BooleanField(default=False)
    form_schema = fields.JSONField()
    
    # Add the category field with the correct CharEnumField type
    category = fields.CharEnumField(
        AccountCategoryEnum,
        max_length=50,
        null=True,
        description="The category of the account type"
    )
    countries = fields.ManyToManyField(
        "models.Country",
        related_name="account_types",
        through="country_account_types",
        forward_key="account_type_id",  # apunta a account_types.id (integer)
        backward_key="country_id",      # apunta a country.country_id (uuid)
        through_fields=("account_type_id", "country_id")  
    )

    class Meta:
        table = "account_types"

    def __str__(self):
        return self.name