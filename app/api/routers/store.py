from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Path, Query
from fastapi.responses import JSONResponse, Response

from app.schemas.store import StoreCreate, StoreDB, StoreUpdate, StoreWithCountry
from app.schemas.user import UserUpdate
from app.schemas.user_out import UserOut
from app.services.store import store_service
from app.services.user import user_service

router = APIRouter()


@router.get(
    "/",
    response_class=JSONResponse,
    response_model=List[StoreWithCountry],
    status_code=200,
)
async def get_all_stores(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    admin_id: Optional[UUID] = None,
):
    """Obtener todas las tiendas con información del país incluida"""
    stores = await store_service.get_all_with_country(skip=skip, limit=limit)
    return stores


@router.post(
    "/",
    response_class=JSONResponse,
    response_model=StoreDB,
    status_code=201,
)
async def create_store(
    new_store: StoreCreate,
    admin_id: Optional[UUID] = None,
):
    store = await store_service.create(obj_in=new_store)
    return store


@router.get(
    "/{store_id}",
    response_class=JSONResponse,
    response_model=StoreWithCountry,
    status_code=200,
)
async def get_store_by_id(
    store_id: UUID = Path(...),
    admin_id: Optional[UUID] = None,
):
    """Obtener una tienda específica con información del país incluida"""
    store = await store_service.get_with_country(id=store_id)
    if store is None:
        raise HTTPException(status_code=404, detail="Store not found")
    return store


@router.patch(
    "/{store_id}",
    response_class=Response,
    status_code=204,
)
async def update_store(
    update_store: StoreUpdate,
    store_id: UUID = Path(...),
    admin_id: Optional[UUID] = None,
):
    await store_service.update(id=store_id, obj_in=update_store)


@router.delete(
    "/{store_id}",
    response_class=Response,
    status_code=204,
)
async def delete_store(
    store_id: UUID = Path(...),
    admin_id: Optional[UUID] = None,
):
    deleted = await store_service.delete(id=store_id)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Store not found")


@router.get(
    "/{store_id}/users",
    response_class=JSONResponse,
    response_model=List[UserOut],
    status_code=200,
)
async def get_store_users(
    store_id: UUID = Path(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """Obtener todos los usuarios asociados a una tienda específica"""
    # Verificar que la tienda existe
    store = await store_service.get(id=store_id)
    if store is None:
        raise HTTPException(status_code=404, detail="Store not found")
    
    # Obtener usuarios de la tienda
    filters = {"store_id": store_id}
    users = await user_service.get_all(payload=filters, skip=skip, limit=limit)
    return users


@router.post(
    "/{store_id}/users/{user_id}",
    response_class=Response,
    status_code=204,
)
async def assign_user_to_store(
    store_id: UUID = Path(...),
    user_id: UUID = Path(...),
):
    """Asignar un usuario a una tienda específica"""
    # Verificar que la tienda existe
    store = await store_service.get(id=store_id)
    if store is None:
        raise HTTPException(status_code=404, detail="Store not found")
    
    # Verificar que el usuario existe
    user = await user_service.get(id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Actualizar el usuario con el store_id
    user_update = UserUpdate(store_id=store_id)
    await user_service.update(id=user_id, obj_in=user_update)


@router.delete(
    "/{store_id}/users/{user_id}",
    response_class=Response,
    status_code=204,
)
async def remove_user_from_store(
    store_id: UUID = Path(...),
    user_id: UUID = Path(...),
):
    """Eliminar la asociación de un usuario con una tienda"""
    # Verificar que la tienda existe
    store = await store_service.get(id=store_id)
    if store is None:
        raise HTTPException(status_code=404, detail="Store not found")
    
    # Verificar que el usuario existe y pertenece a la tienda
    user = await user_service.get(id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.store_id != store_id:
        raise HTTPException(status_code=400, detail="User is not associated with this store")
    
    # Actualizar el usuario quitando el store_id
    user_update = UserUpdate(store_id=None)
    await user_service.update(id=user_id, obj_in=user_update)
