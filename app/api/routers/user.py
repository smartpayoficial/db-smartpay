from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import JSONResponse, Response
from passlib.context import CryptContext

from app.schemas.user import UserCreate, UserDB, UserUpdate
from app.services.user import user_service

router = APIRouter()

# bcrypt context
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get(
    "",
    response_class=JSONResponse,
    response_model=List[UserDB],
    status_code=200,
)
async def get_all_users():
    """Get all users"""
    users = await user_service.get_all()
    return users


@router.post(
    "",
    response_class=JSONResponse,
    response_model=UserDB,
    status_code=201,
)
async def create_user(new_user: UserCreate):
    """Create a new user (hashes password before storing)"""
    data = new_user.dict()
    data["password"] = pwd_ctx.hash(new_user.password)
    user = await user_service.create(obj_in=UserCreate(**data))
    return user


@router.get(
    "/{user_id}",
    response_class=JSONResponse,
    response_model=UserDB,
    status_code=200,
)
async def get_user_by_id(user_id: UUID = Path(...)):
    """Get a user by ID"""
    user = await user_service.get_by_id(id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch(
    "/{user_id}",
    response_class=Response,
    status_code=204,
)
async def update_user(update_user: UserUpdate, user_id: UUID = Path(...)):
    """Update a user. If password provided, hash it."""
    data = update_user.dict(exclude_unset=True)
    if "password" in data:
        data["password"] = pwd_ctx.hash(data["password"])
    await user_service.update(id=user_id, obj_in=UserUpdate(**data))


@router.delete(
    "/{user_id}",
    response_class=Response,
    status_code=204,
)
async def delete_user(user_id: UUID = Path(...)):
    """Delete a user"""
    deleted = await user_service.delete(id=user_id)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="User not found")
