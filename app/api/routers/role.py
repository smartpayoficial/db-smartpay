from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Path, Query
from fastapi.responses import JSONResponse, Response

from app.schemas.role import RoleCreate, RoleDB, RoleUpdate
from app.services.role import role_service

router = APIRouter()


@router.get(
    "/",
    response_class=JSONResponse,
    response_model=List[RoleDB],
    status_code=200,
)
async def get_all_roles(
    name: str = Query(None, description="Filtrar por nombre de rol")
):
    payload = {}
    if name:
        payload["name__icontains"] = name
    roles = await role_service.get_all(payload=payload)
    return roles


@router.post(
    "/",
    response_class=JSONResponse,
    response_model=RoleDB,
    status_code=201,
)
async def create_role(new_role: RoleCreate):
    role = await role_service.create(obj_in=new_role)
    return role


@router.get(
    "/{role_id}",
    response_class=JSONResponse,
    response_model=RoleDB,
    status_code=200,
)
async def get_role_by_id(role_id: UUID = Path(...)):
    role = await role_service.get(id=role_id)
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.patch(
    "/{role_id}",
    response_class=Response,
    status_code=204,
)
async def update_role(update_role: RoleUpdate, role_id: UUID = Path(...)):
    await role_service.update(id=role_id, obj_in=update_role)


@router.delete(
    "/{role_id}",
    response_class=Response,
    status_code=204,
)
async def delete_role(role_id: UUID = Path(...)):
    deleted = await role_service.delete(id=role_id)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Role not found")
