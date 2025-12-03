from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.infra.postgres.models.device import DeviceState
from app.schemas.enrolment import EnrolmentResponse


class TelevisionBase(BaseModel):
    brand: str
    model: str
    android_version: int
    serial_number: str
    board: str
    fingerprint: str
    state: DeviceState = DeviceState.ACTIVE


class TelevisionCreate(TelevisionBase):
    enrolment_id: UUID


class TelevisionUpdate(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None
    android_version: Optional[int] = None
    serial_number: Optional[str] = None
    board: Optional[str] = None
    fingerprint: Optional[str] = None
    state: Optional[DeviceState] = None
    enrolment_id: Optional[UUID] = None


class TelevisionDB(TelevisionBase):
    television_id: UUID
    enrolment_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class TelevisionResponse(TelevisionBase):
    television_id: UUID
    enrolment: EnrolmentResponse
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
