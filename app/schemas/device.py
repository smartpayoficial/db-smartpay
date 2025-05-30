from uuid import UUID

from pydantic import BaseModel


class DeviceBase(BaseModel):
    name: str
    description: str
    type: str
    status: str


class DeviceCreate(DeviceBase):
    pass


class DeviceUpdate(DeviceBase):
    pass


class DeviceDB(DeviceBase):
    device_id: UUID

    class Config:
        orm_mode = True
