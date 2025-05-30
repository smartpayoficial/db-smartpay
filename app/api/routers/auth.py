from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import JSONResponse, Response

from app.schemas.auth import (
    AuthenticationCreate,
    AuthenticationDB,
    AuthenticationUpdate,
    ConfigurationCreate,
    ConfigurationDB,
    ConfigurationUpdate,
    RoleCreate,
    RoleDB,
    RoleUpdate,
)
from app.services.auth import auth_service, config_service, role_service

# Role Router
router_role = APIRouter()


@router_role.get(
    "",
    response_class=JSONResponse,
    response_model=List[RoleDB],
    status_code=200,
)
async def get_all_roles():
    roles = await role_service.get_all()
    return roles


@router_role.post(
    "",
    response_class=JSONResponse,
    response_model=RoleDB,
    status_code=201,
)
async def create_role(new_role: RoleCreate):
    role = await role_service.create(obj_in=new_role)
    return role


@router_role.get(
    "/{role_id}",
    response_class=JSONResponse,
    response_model=RoleDB,
    status_code=200,
)
async def get_role_by_id(role_id: UUID = Path(...)):
    role = await role_service.get_by_id(id=role_id)
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router_role.patch(
    "/{role_id}",
    response_class=Response,
    status_code=204,
)
async def update_role(update_role: RoleUpdate, role_id: UUID = Path(...)):
    await role_service.update(id=role_id, obj_in=update_role)


@router_role.delete(
    "/{role_id}",
    response_class=Response,
    status_code=204,
)
async def delete_role(role_id: UUID = Path(...)):
    deleted = await role_service.delete(id=role_id)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Role not found")


# Configuration Router
router_config = APIRouter()


@router_config.get(
    "",
    response_class=JSONResponse,
    response_model=List[ConfigurationDB],
    status_code=200,
)
async def get_all_configs():
    configs = await config_service.get_all()
    return configs


@router_config.post(
    "",
    response_class=JSONResponse,
    response_model=ConfigurationDB,
    status_code=201,
)
async def create_config(new_config: ConfigurationCreate):
    config = await config_service.create(obj_in=new_config)
    return config


@router_config.get(
    "/{config_id}",
    response_class=JSONResponse,
    response_model=ConfigurationDB,
    status_code=200,
)
async def get_config_by_id(config_id: UUID = Path(...)):
    config = await config_service.get_by_id(id=config_id)
    if config is None:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return config


@router_config.patch(
    "/{config_id}",
    response_class=Response,
    status_code=204,
)
async def update_config(
    update_config: ConfigurationUpdate, config_id: UUID = Path(...)
):
    await config_service.update(id=config_id, obj_in=update_config)


@router_config.delete(
    "/{config_id}",
    response_class=Response,
    status_code=204,
)
async def delete_config(config_id: UUID = Path(...)):
    deleted = await config_service.delete(id=config_id)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Configuration not found")


# Authentication Router
router_auth = APIRouter()


@router_auth.get(
    "",
    response_class=JSONResponse,
    response_model=List[AuthenticationDB],
    status_code=200,
)
async def get_all_auths():
    auths = await auth_service.get_all()
    return auths


@router_auth.post(
    "",
    response_class=JSONResponse,
    response_model=AuthenticationDB,
    status_code=201,
)
async def create_auth(new_auth: AuthenticationCreate):
    auth = await auth_service.create(obj_in=new_auth)
    return auth


@router_auth.get(
    "/{auth_id}",
    response_class=JSONResponse,
    response_model=AuthenticationDB,
    status_code=200,
)
async def get_auth_by_id(auth_id: UUID = Path(...)):
    auth = await auth_service.get_by_id(id=auth_id)
    if auth is None:
        raise HTTPException(status_code=404, detail="Authentication not found")
    return auth


@router_auth.patch(
    "/{auth_id}",
    response_class=Response,
    status_code=204,
)
async def update_auth(update_auth: AuthenticationUpdate, auth_id: UUID = Path(...)):
    await auth_service.update(id=auth_id, obj_in=update_auth)


@router_auth.delete(
    "/{auth_id}",
    response_class=Response,
    status_code=204,
)
async def delete_auth(auth_id: UUID = Path(...)):
    deleted = await auth_service.delete(id=auth_id)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Authentication not found")
