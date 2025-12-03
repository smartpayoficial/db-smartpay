from enum import Enum
from typing import List, Optional, Any
from pydantic import BaseModel


class AccountCategoryEnum(str, Enum):
    CONTACT = "CONTACT"
    BANK_ACCOUNT = "BANK_ACCOUNT"
    MOBILE_PAYMENT = "MOBILE_PAYMENT"
    PAYMENT_GATEWAY = "PAYMENT_GATEWAY"
    PUBLIC_PROFILE = "PUBLIC_PROFILE"
    WEBHOOK = "WEBHOOK"
    LOCATION = "LOCATION"


class AccountTypeBase(BaseModel):
    name: str
    description: Optional[str] = None
    icon_url: Optional[str] = None
    is_international: bool = False
    form_schema: List[Any]
    category: Optional[AccountCategoryEnum] = None


class AccountTypeCreate(AccountTypeBase):
    category: AccountCategoryEnum


class AccountTypeUpdate(AccountTypeBase):
    pass


class AccountTypeInDB(AccountTypeBase):
    id: int

    class Config:
        orm_mode = True


class AccountTypeDB(AccountTypeInDB):
    pass
