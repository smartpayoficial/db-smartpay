from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class PaymentState(str, Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    FAILED = "Failed"
    RETURNED = "Returned"


class PlanBase(BaseModel):
    user_id: UUID
    vendor_id: UUID
    device_id: UUID
    initial_date: date
    quotas: int
    contract: str


class PlanCreate(PlanBase):
    pass


class PlanUpdate(PlanBase):
    pass


class PlanDB(PlanBase):
    plan_id: UUID

    class Config:
        orm_mode = True


class PaymentBase(BaseModel):
    device_id: UUID
    plan_id: UUID
    value: Decimal
    method: str
    state: PaymentState
    date: datetime
    reference: str


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(PaymentBase):
    pass


class PaymentDB(PaymentBase):
    payment_id: UUID

    class Config:
        orm_mode = True
