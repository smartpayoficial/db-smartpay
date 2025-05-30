from uuid import UUID

from pydantic import BaseModel


class AuthenticationBase(BaseModel):
    username: str
    password: str
    email: str


class AuthenticationCreate(AuthenticationBase):
    pass


class AuthenticationUpdate(AuthenticationBase):
    pass


class AuthenticationDB(AuthenticationBase):
    authentication_id: UUID

    class Config:
        orm_mode = True
