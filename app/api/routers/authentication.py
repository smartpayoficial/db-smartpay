from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import JSONResponse, Response

from app.schemas.authentication import (
    AuthenticationCreate,
    AuthenticationDB,
    AuthenticationUpdate,
)
from app.services.authentication import authentication_service

router = APIRouter()


@router.get(
    "",
    response_class=JSONResponse,
    response_model=List[AuthenticationDB],
    status_code=200,
)
async def get_all_authentications():
    authentications = await authentication_service.get_all()
    return authentications


@router.post(
    "",
    response_class=JSONResponse,
    response_model=AuthenticationDB,
    status_code=201,
)
async def create_authentication(new_authentication: AuthenticationCreate):
    authentication = await authentication_service.create(obj_in=new_authentication)
    return authentication


@router.get(
    "/{authentication_id}",
    response_class=JSONResponse,
    response_model=AuthenticationDB,
    status_code=200,
)
async def get_authentication_by_id(authentication_id: UUID = Path(...)):
    authentication = await authentication_service.get_by_id(id=authentication_id)
    if authentication is None:
        raise HTTPException(status_code=404, detail="Authentication not found")
    return authentication


@router.patch(
    "/{authentication_id}",
    response_class=Response,
    status_code=204,
)
async def update_authentication(
    update_authentication: AuthenticationUpdate, authentication_id: UUID = Path(...)
):
    await authentication_service.update(
        id=authentication_id, obj_in=update_authentication
    )


@router.delete(
    "/{authentication_id}",
    response_class=Response,
    status_code=204,
)
async def delete_authentication(authentication_id: UUID = Path(...)):
    deleted = await authentication_service.delete(id=authentication_id)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Authentication not found")
