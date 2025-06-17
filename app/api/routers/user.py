from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import JSONResponse, Response
from passlib.context import CryptContext

from app.schemas.user import UserCreate, UserUpdate
from app.schemas.user_out import RoleOut, UserOut
from app.services.user import user_service

router = APIRouter()

# bcrypt context
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get(
    "",
    response_class=JSONResponse,
    response_model=List[UserOut],
    status_code=200,
)
async def get_all_users():
    """Get all users with resolved role"""

    users = await user_service.get_all()
    user_out_list = []
    for user in users:
        role_out = (
            RoleOut(
                role_id=str(user["role__role_id"]),
                name=user["role__name"],
                description=user["role__description"],
            )
            if user.get("role__role_id")
            else None
        )
        city_dict = None  # Si necesitas resolver city, aquí puedes hacerlo
        user_out = UserOut(
            user_id=str(user["user_id"]),
            city=city_dict,
            dni=user["dni"],
            first_name=user["first_name"],
            middle_name=user.get("middle_name"),
            last_name=user["last_name"],
            second_last_name=user.get("second_last_name"),
            email=user["email"],
            prefix=user["prefix"],
            phone=user["phone"],
            address=user["address"],
            username=user["username"],
            state=user["state"],
            created_at=(
                user["created_at"].isoformat() if user.get("created_at") else None
            ),
            updated_at=(
                user["updated_at"].isoformat() if user.get("updated_at") else None
            ),
            role=role_out,
        )
        user_out_list.append(user_out)
    return user_out_list


@router.post(
    "",
    response_class=JSONResponse,
    response_model=UserOut,
    status_code=201,
)
async def create_user(new_user: UserCreate):
    """Create a new user (hashes password before storing)"""
    data = new_user.dict()
    data["password"] = pwd_ctx.hash(new_user.password)
    user = await user_service.create(obj_in=UserCreate(**data))
    user_out = UserOut(
        user_id=str(user["user_id"]) if isinstance(user, dict) else str(user.user_id),
        city=None,  # Ajusta si tienes info de city
        dni=user["dni"] if isinstance(user, dict) else user.dni,
        first_name=user["first_name"] if isinstance(user, dict) else user.first_name,
        middle_name=(
            user.get("middle_name")
            if isinstance(user, dict)
            else getattr(user, "middle_name", None)
        ),
        last_name=user["last_name"] if isinstance(user, dict) else user.last_name,
        second_last_name=(
            user.get("second_last_name")
            if isinstance(user, dict)
            else getattr(user, "second_last_name", None)
        ),
        email=user["email"] if isinstance(user, dict) else user.email,
        prefix=user["prefix"] if isinstance(user, dict) else user.prefix,
        phone=user["phone"] if isinstance(user, dict) else user.phone,
        address=user["address"] if isinstance(user, dict) else user.address,
        username=user["username"] if isinstance(user, dict) else user.username,
        state=str(user["state"]) if isinstance(user, dict) else str(user.state),
        created_at=(
            (user["created_at"].isoformat() if user.get("created_at") else None)
            if isinstance(user, dict)
            else (
                user.created_at.isoformat()
                if getattr(user, "created_at", None)
                else None
            )
        ),
        updated_at=(
            (user["updated_at"].isoformat() if user.get("updated_at") else None)
            if isinstance(user, dict)
            else (
                user.updated_at.isoformat()
                if getattr(user, "updated_at", None)
                else None
            )
        ),
        role=(
            RoleOut(
                role_id=str(user["role__role_id"]),
                name=user["role__name"],
                description=user["role__description"],
            )
            if (isinstance(user, dict) and user.get("role__role_id"))
            else None
        ),
    )
    return user_out


@router.get(
    "/{user_id}",
    response_class=JSONResponse,
    response_model=UserOut,
    status_code=200,
)
async def get_user_by_id(user_id: UUID = Path(...)):
    """Get a user by ID"""
    user = await user_service.get_by_id(id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user_out = UserOut(
        user_id=str(user["user_id"]) if isinstance(user, dict) else str(user.user_id),
        city=None,  # Ajusta si tienes info de city
        dni=user["dni"] if isinstance(user, dict) else user.dni,
        first_name=user["first_name"] if isinstance(user, dict) else user.first_name,
        middle_name=(
            user.get("middle_name")
            if isinstance(user, dict)
            else getattr(user, "middle_name", None)
        ),
        last_name=user["last_name"] if isinstance(user, dict) else user.last_name,
        second_last_name=(
            user.get("second_last_name")
            if isinstance(user, dict)
            else getattr(user, "second_last_name", None)
        ),
        email=user["email"] if isinstance(user, dict) else user.email,
        prefix=user["prefix"] if isinstance(user, dict) else user.prefix,
        phone=user["phone"] if isinstance(user, dict) else user.phone,
        address=user["address"] if isinstance(user, dict) else user.address,
        username=user["username"] if isinstance(user, dict) else user.username,
        state=str(user["state"]) if isinstance(user, dict) else str(user.state),
        created_at=(
            (user["created_at"].isoformat() if user.get("created_at") else None)
            if isinstance(user, dict)
            else (
                user.created_at.isoformat()
                if getattr(user, "created_at", None)
                else None
            )
        ),
        updated_at=(
            (user["updated_at"].isoformat() if user.get("updated_at") else None)
            if isinstance(user, dict)
            else (
                user.updated_at.isoformat()
                if getattr(user, "updated_at", None)
                else None
            )
        ),
        role=(
            RoleOut(
                role_id=str(user["role__role_id"]),
                name=user["role__name"],
                description=user["role__description"],
            )
            if (isinstance(user, dict) and user.get("role__role_id"))
            else None
        ),
    )
    return user_out


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
