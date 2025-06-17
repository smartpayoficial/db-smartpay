from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class GroupState(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"


class GroupBase(BaseModel):
    name: str
    state: GroupState = GroupState.ACTIVE


class GroupCreate(GroupBase):
    pass


class GroupUpdate(BaseModel):
    name: Optional[str] = None
    state: Optional[GroupState] = None


class GroupDB(GroupBase):
    group_id: UUID

    class Config:
        orm_mode = True


class DeviceGroupBase(BaseModel):
    device_id: UUID
    group_id: UUID


class DeviceGroupCreate(DeviceGroupBase):
    pass


class DeviceGroupUpdate(BaseModel):
    device_id: Optional[UUID] = None
    group_id: Optional[UUID] = None


class DeviceGroupDB(DeviceGroupBase):
    device_group_id: UUID

    class Config:
        orm_mode = True


class EnrolmentBase(BaseModel):
    user_id: UUID
    vendor_id: UUID


class EnrolmentCreate(EnrolmentBase):
    pass


class EnrolmentUpdate(EnrolmentBase):
    pass


class EnrolmentDB(EnrolmentBase):
    enrolment_id: UUID

    class Config:
        orm_mode = True
