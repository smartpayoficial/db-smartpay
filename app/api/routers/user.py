from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Path, Query
from fastapi.responses import JSONResponse, Response
from passlib.context import CryptContext

from app.schemas.user import UserCreate, UserUpdate
from app.schemas.user_out import UserOut
from app.services.user import user_service

router = APIRouter()

# bcrypt context
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get(
    "/",
    response_class=JSONResponse,
    response_model=List[UserOut],
    status_code=200,
)
async def get_all_users(
    role_name: Optional[str] = Query(None, description="Filtrar por nombre de rol"),
    state: Optional[str] = Query(None, description="Filtrar por estado del usuario (Active/Inactive)"),
    name: Optional[str] = Query(None, description="Filtrar por nombre o apellido del usuario"),
    skip: int = 0,
    limit: int = 100,
):
    """Obtiene todos los usuarios con sus roles resueltos. Permite filtrar y paginar."""
    payload = {}
    if role_name:
        payload["role__name__iexact"] = role_name
    if state:
        payload["state__iexact"] = state
    if name:
        # Implementamos una búsqueda que incluya tanto nombre como apellido
        from tortoise.expressions import Q
        return await user_service.get_all_with_filter(
            Q(first_name__icontains=name) | Q(last_name__icontains=name),
            payload=payload,
            skip=skip,
            limit=limit
        )

    users = await user_service.get_all(payload=payload, skip=skip, limit=limit)
    return users


@router.post(
    "/",
    response_class=JSONResponse,
    response_model=UserOut,
    status_code=201,
)
async def create_user(new_user: UserCreate):
    """Crea un nuevo usuario (hashea la contraseña antes de guardarla)."""
    hashed_password = pwd_ctx.hash(new_user.password)
    user_data_with_hashed_pass = new_user.copy(update={"password": hashed_password})

    user = await user_service.create(obj_in=user_data_with_hashed_pass)
    return user


@router.get(
    "/{user_id}",
    response_class=JSONResponse,
    response_model=UserOut,
    status_code=200,
)
async def get_user_by_id(user_id: UUID = Path(...)):
    """Obtiene un usuario por su ID."""
    user = await user_service.get(id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch(
    "/{user_id}",
    response_class=JSONResponse,
    response_model=UserOut,
    status_code=200,
)
async def update_user(user_id: UUID, user_in: UserUpdate):
    """Actualiza un usuario."""
    if user_in.password:
        user_in.password = pwd_ctx.hash(user_in.password)

    user = await user_service.update(id=user_id, obj_in=user_in)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete(
    "/{user_id}",
    status_code=204,
)
async def delete_user(user_id: UUID):
    """Elimina un usuario."""
    deleted = await user_service.delete(id=user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return Response(status_code=204)


@router.get(
    "/by-dni/{dni}",
    response_class=JSONResponse,
    response_model=UserOut,
    status_code=200,
)
async def get_user_by_dni(dni: str = Path(..., description="DNI del usuario")):
    """Obtiene un usuario por su DNI."""
    user = await user_service.get_by_dni(dni=dni)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get(
    "/by-email/{email}",
    response_class=JSONResponse,
    response_model=UserOut,
    status_code=200,
)
async def get_user_by_email(email: str = Path(..., description="Email del usuario")):
    """Obtiene un usuario por su email."""
    user = await user_service.get_by_email(email=email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
