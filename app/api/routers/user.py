from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from fastapi.responses import JSONResponse, Response

from app.schemas.user import CreateUser, SearchUser, UpdateUser, UserDB
from app.services.user import user_service

router = APIRouter()


@router.get(
    "",
    response_class=JSONResponse,
    response_model=List[UserDB],
    status_code=200,
    responses={
        200: {"description": "Users found"},
    },
)
async def get_all(
    skip: int = Query(0),
    limit: int = Query(10),
    search: SearchUser = Depends(SearchUser),
):
    users = await user_service.get_all(
        skip=skip, limit=limit, payload=search.dict(exclude_none=True)
    )
    return users


@router.post(
    "",
    response_class=JSONResponse,
    response_model=UserDB,
    status_code=201,
    responses={
        201: {"description": "User created"},
    },
)
async def create(new_user: CreateUser):
    user = await user_service.create(obj_in=new_user)
    return user


@router.get(
    "/{_id}",
    response_class=JSONResponse,
    response_model=UserDB,
    status_code=200,
    responses={
        200: {"description": "User found"},
        404: {"description": "User not found"},
    },
)
async def by_id(_id: int = Path(...)):
    user = await user_service.get_by_id(_id=_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch(
    "/{_id}",
    response_class=Response,
    response_model=None,
    status_code=204,
    responses={
        204: {"description": "User updated"},
        404: {"description": "User not found"},
    },
)
async def update(update_user: UpdateUser, _id: int = Path(...)):
    await user_service.update(_id=_id, obj_in=update_user)


@router.delete(
    "/{_id}",
    response_class=Response,
    response_model=None,
    status_code=204,
    responses={
        204: {"description": "User deleted"},
    },
)
async def delete(_id: int = Path(...)):
    user = await user_service.delete(_id=_id)
    if user == 0:
        raise HTTPException(status_code=404, detail="User not found")
