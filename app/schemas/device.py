from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from app.schemas.enrolment import EnrolmentResponse

from app.infra.postgres.models.device import DeviceState


class DeviceBase(BaseModel):
    name: str
    imei: str
    imei_two: str
    serial_number: str
    model: str
    brand: str
    product_name: str
    state: DeviceState = (
        DeviceState.ACTIVE
    )  # Only 'Active' or 'Inactive' allowed (enforced by DeviceState enum)


class DeviceCreate(DeviceBase):
    enrolment_id: UUID


class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    imei: Optional[str] = None
    imei_two: Optional[str] = None
    serial_number: Optional[str] = None
    model: Optional[str] = None
    brand: Optional[str] = None
    product_name: Optional[str] = None
    state: Optional[DeviceState] = None
    enrolment_id: Optional[UUID] = None


class DeviceDB(DeviceBase):
    device_id: UUID
    enrolment_id: UUID

    class Config:
        orm_mode = True


class DeviceResponse(DeviceBase):
    device_id: UUID
    enrolment: EnrolmentResponse

    class Config:
        orm_mode = True
