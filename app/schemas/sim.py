from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SimBase(BaseModel):
    device_id: UUID = Field(..., description="ID of the associated device")
    icc_id: str = Field(..., max_length=30, description="ICC ID of the SIM card")
    slot_index: str = Field(
        ..., max_length=10, description="Slot index where the SIM is inserted"
    )
    operator: str = Field(..., max_length=50, description="Mobile network operator")
    number: str = Field(..., max_length=20, description="Phone number of the SIM card")
    state: str = Field(
        "Active", max_length=20, description="Current state of the SIM card"
    )


class SimCreate(SimBase):
    pass


class SimUpdate(BaseModel):
    device_id: Optional[UUID] = Field(None, description="ID of the associated device")
    icc_id: Optional[str] = Field(
        None, max_length=30, description="ICC ID of the SIM card"
    )
    slot_index: Optional[str] = Field(
        None, max_length=10, description="Slot index where the SIM is inserted"
    )
    operator: Optional[str] = Field(
        None, max_length=50, description="Mobile network operator"
    )
    number: Optional[str] = Field(
        None, max_length=20, description="Phone number of the SIM card"
    )
    state: Optional[str] = Field(
        None, max_length=20, description="Current state of the SIM card"
    )


class SimInDBBase(SimBase):
    sim_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Sim(SimInDBBase):
    pass


class SimInDB(SimInDBBase):
    pass
