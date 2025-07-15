from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import JSONResponse, Response

from app.schemas.store import StoreCreate, StoreDB, StoreUpdate
from app.services.store import store_service

router = APIRouter()


@router.get(
    "/",
    response_class=JSONResponse,
    response_model=List[StoreDB],
    status_code=200,
)
async def get_all_stores():
    stores = await store_service.get_all()
    return stores


@router.post(
    "/",
    response_class=JSONResponse,
    response_model=StoreDB,
    status_code=201,
)
async def create_store(new_store: StoreCreate):
    store = await store_service.create(obj_in=new_store)
    return store


@router.get(
    "/{store_id}",
    response_class=JSONResponse,
    response_model=StoreDB,
    status_code=200,
)
async def get_store_by_id(store_id: UUID = Path(...)):
    store = await store_service.get(id=store_id)
    if store is None:
        raise HTTPException(status_code=404, detail="Store not found")
    return store


@router.patch(
    "/{store_id}",
    response_class=Response,
    status_code=204,
)
async def update_store(update_store: StoreUpdate, store_id: UUID = Path(...)):
    await store_service.update(id=store_id, obj_in=update_store)


@router.delete(
    "/{store_id}",
    response_class=Response,
    status_code=204,
)
async def delete_store(store_id: UUID = Path(...)):
    deleted = await store_service.delete(id=store_id)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Store not found")
