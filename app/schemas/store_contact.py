from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel
from .account_type import AccountTypeDB

class StoreContactBase(BaseModel):
    account_type_id: int
    contact_details: Dict[str, Any]
    description: Optional[str] = None

class StoreContactCreate(StoreContactBase):
    store_id: UUID

class StoreContactUpdate(BaseModel):
    contact_details: Optional[Dict[str, Any]] = None
    description: Optional[str] = None

class StoreContactInDB(StoreContactBase):
    id: UUID
    store_id: UUID
    account_type: AccountTypeDB

    class Config:
        orm_mode = True

class StoreContactDB(StoreContactInDB):
    pass
