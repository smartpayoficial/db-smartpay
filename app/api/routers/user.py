from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import JSONResponse, Response
from passlib.context import CryptContext
import logging
logger = logging.getLogger("uvicorn.error")

from app.schemas.user import UserCreate, UserUpdate
from app.schemas.user_out import RoleOut, UserOut
from app.services.user import user_service

router = APIRouter()

# bcrypt context
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


from fastapi import Query

@router.get(
    "",
    response_class=JSONResponse,
    response_model=List[UserOut],
    status_code=200,
)
async def get_all_users(
    role_name: str = Query(None, description="Filtrar por nombre de rol"),
    state: str = Query(None, description="Filtrar por estado del usuario (Active/Inactive)")
):
    """Get all users with resolved role. Permite filtrar por role_name y state."""

    filter_payload = {}
    if role_name:
        filter_payload["role__name__iexact"] = role_name
    if state:
        filter_payload["state__iexact"] = state
    users = await user_service.get_all(payload=filter_payload)
    user_out_list = []
    for user in users:
        role_out = (
            RoleOut(
                role_id=str(user["role__role_id"]),
                name=user["role__name"],
                description=user["role__description"],
            )
            if user.get("role__role_id")
            else (_ for _ in ()).throw(HTTPException(status_code=500, detail="El usuario no tiene un rol asociado correctamente en la base de datos."))
        )
        logger.info(f"[DEBUG] user_id={user['user_id']} city__city_id={user.get('city__city_id')} city__name={user.get('city__name')}")
        city_dict = (
            {"city_id": str(user["city__city_id"]), "name": user["city__name"]}
            if user.get("city__city_id") and user.get("city__name") else None
        )
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
            created_at=(user["created_at"].isoformat() if user.get("created_at") else None),
            updated_at=(user["updated_at"].isoformat() if user.get("updated_at") else None),
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
    # Si user es QuerySet, conviértelo a dict o extrae el primer elemento
    from tortoise.queryset import QuerySet
    if 'QuerySet' in str(type(user)):
        # Forzamos a obtener el primer elemento como dict
        user = await user.first().values() if hasattr(user, 'first') and hasattr(user, 'values') else None
        if isinstance(user, list) and user:
            user = user[0]
        elif isinstance(user, list):
            user = None
    # Soporta tanto dict como modelo para city
    if isinstance(user, dict):
        city_value = (
            {"city_id": str(user["city__city_id"]), "name": user["city__name"]}
            if user.get("city__city_id") and user.get("city__name") else None
        )
        role_out = (
            RoleOut(
                role_id=str(user["role__role_id"]),
                name=user["role__name"],
                description=user["role__description"],
            )
            if user.get("role__role_id") and user.get("role__name") and user.get("role__description") else None
        )
        debug_user_id = user.get("user_id")
        debug_city_id = user.get("city__city_id")
        debug_city_name = user.get("city__name")
    else:
        city_id = getattr(user, "city__city_id", getattr(user, "city_id", None))
        city_name = getattr(user, "city__name", getattr(user, "city", None))
        city_value = (
            {"city_id": str(city_id), "name": city_name}
            if city_id and city_name else None
        )
        role_id = getattr(user, "role__role_id", getattr(user, "role_id", None))
        role_name = getattr(user, "role__name", getattr(user, "role", None))
        role_desc = getattr(user, "role__description", getattr(user, "role_description", None))
        role_out = (
            RoleOut(
                role_id=str(role_id),
                name=role_name,
                description=role_desc,
            )
            if role_id and role_name and role_desc else None
        )
        debug_user_id = getattr(user, "user_id", None)
        debug_city_id = getattr(user, "city__city_id", getattr(user, "city_id", None))
        debug_city_name = getattr(user, "city__name", getattr(user, "city", None))

    user_out = UserOut(
        user_id=str(debug_user_id),
        city=city_value,
        dni=user["dni"] if isinstance(user, dict) else user.dni,
        first_name=user["first_name"] if isinstance(user, dict) else user.first_name,
        middle_name=(user.get("middle_name") if isinstance(user, dict) else getattr(user, "middle_name", None)),
        last_name=user["last_name"] if isinstance(user, dict) else user.last_name,
        second_last_name=(user.get("second_last_name") if isinstance(user, dict) else getattr(user, "second_last_name", None)),
        email=user["email"] if isinstance(user, dict) else user.email,
        prefix=user["prefix"] if isinstance(user, dict) else user.prefix,
        phone=user["phone"] if isinstance(user, dict) else user.phone,
        address=user["address"] if isinstance(user, dict) else user.address,
        username=user["username"] if isinstance(user, dict) else user.username,
        state=str(user["state"]) if isinstance(user, dict) else str(user.state),
        created_at=(user["created_at"].isoformat() if isinstance(user, dict) and user.get("created_at") else (user.created_at.isoformat() if getattr(user, "created_at", None) else None)),
        updated_at=(user["updated_at"].isoformat() if isinstance(user, dict) and user.get("updated_at") else (user.updated_at.isoformat() if getattr(user, "updated_at", None) else None)),
        role=role_out,
    )
    print(f"[DEBUG] user_id={debug_user_id} city__city_id={debug_city_id} city__name={debug_city_name}")
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
    logger.info(f"[DEBUG] user_id={user['user_id']} city__city_id={user.get('city__city_id')} city__name={user.get('city__name')}")
    city_value = (
        {"city_id": str(user["city__city_id"]), "name": user["city__name"]}
        if user.get("city__city_id") and user.get("city__name") else None
    )
    user_out = UserOut(
        user_id=str(user["user_id"]) if isinstance(user, dict) else str(user.user_id),
        city=city_value, 
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
    response_class=JSONResponse,
    response_model=UserOut,
    status_code=200,
)
async def update_user(update_user: UserUpdate, user_id: UUID = Path(...)):
    """Update a user. If password provided, hash it. Only fields sent will be updated."""
    data = update_user.dict(exclude_unset=True)
    if "password" in data:
        data["password"] = pwd_ctx.hash(data["password"])
    updated = await user_service.update(id=user_id, obj_in=UserUpdate(**data))
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    # Recupera y devuelve el usuario actualizado
    user = await user_service.get_by_id(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Adaptar los campos para el esquema UserOut
    role_out = None
    if user.get("role__role_id"):
        role_out = RoleOut(
            role_id=str(user["role__role_id"]),
            name=user["role__name"],
            description=user["role__description"]
        )
    city_dict = (
        {"city_id": str(user["city__city_id"]), "name": user["city__name"]}
        if user.get("city__city_id") and user.get("city__name") else None
    )
    return UserOut(
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
        state=str(user["state"]),
        created_at=(user["created_at"].isoformat() if user.get("created_at") else None),
        updated_at=(user["updated_at"].isoformat() if user.get("updated_at") else None),
        role=role_out
    )


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
