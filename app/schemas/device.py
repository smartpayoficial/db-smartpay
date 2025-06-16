from uuid import UUID

from pydantic import BaseModel

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


class DeviceUpdate(DeviceBase):
    pass


class DeviceDB(DeviceBase):
    device_id: UUID
    enrolment_id: UUID

    class Config:
        orm_mode = True
