from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class RoleBase(BaseModel):
    name: str
    description: str


class RoleCreate(RoleBase):
    pass


class RoleResponse(BaseModel):
    role_id: UUID
    name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class RoleDB(RoleBase):
    role_id: UUID

    class Config:
        orm_mode = True


# --- NUEVO: Esquema para la salida de roles ---
class RoleOut(BaseModel):
    role_id: Optional[UUID] = None
    name: Optional[str] = None
    description: Optional[str] = None

    class Config:
        orm_mode = True
