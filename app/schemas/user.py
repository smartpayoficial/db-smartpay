from pydantic import BaseModel


class CreateUser(BaseModel):
    username: str
    password: str
    email: str


class SearchUser(BaseModel):
    username: str


class UpdateUser(BaseModel):
    username: str
    password: str
    email: str


class UserDB(BaseModel):
    id: int
    username: str
    password: str
    email: str

    class Config:
        orm_mode = True
