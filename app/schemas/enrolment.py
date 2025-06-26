from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from app.schemas.user import UserDB


class EnrolmentBase(BaseModel):
    user_id: UUID
    vendor_id: UUID


class EnrolmentCreate(EnrolmentBase):
    pass


class EnrolmentUpdate(BaseModel):
    
    pass


class EnrolmentDB(EnrolmentBase):
    enrolment_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class EnrolmentResponse(BaseModel):
    enrolment_id: UUID
    user: UserDB
    vendor: UserDB
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
