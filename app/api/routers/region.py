from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import JSONResponse, Response

from app.schemas.region import RegionCreate, RegionDB, RegionUpdate
from app.services.region import region_service

router = APIRouter()


@router.get(
    "/",
    response_class=JSONResponse,
    response_model=List[RegionDB],
    status_code=200,
)
async def get_all_regions():
    regions = await region_service.get_all()
    return regions


@router.post(
    "/",
    response_class=JSONResponse,
    response_model=RegionDB,
    status_code=201,
)
async def create_region(new_region: RegionCreate):
    region = await region_service.create(obj_in=new_region)
    return region


@router.get(
    "/{region_id}",
    response_class=JSONResponse,
    response_model=RegionDB,
    status_code=200,
)
async def get_region_by_id(region_id: UUID = Path(...)):
    region = await region_service.get(id=region_id)
    if region is None:
        raise HTTPException(status_code=404, detail="Region not found")
    return region


@router.patch(
    "/{region_id}",
    response_class=Response,
    status_code=204,
)
async def update_region(update_region: RegionUpdate, region_id: UUID = Path(...)):
    # Primero verificamos si la región existe
    region = await region_service.get(id=region_id)
    if region is None:
        raise HTTPException(status_code=404, detail="Region not found")
    
    # Verificamos si hay datos para actualizar
    update_data = update_region.dict(exclude_unset=True)
    if not update_data:
        # Si no hay datos para actualizar, simplemente devolvemos 204 No Content
        return
    
    # Si hay datos para actualizar, procedemos con la actualización
    updated = await region_service.update(id=region_id, obj_in=update_region)
    if not updated:
        # Esto no debería ocurrir ya que verificamos que la región existe
        raise HTTPException(status_code=500, detail="Failed to update region")


@router.delete(
    "/{region_id}",
    response_class=Response,
    status_code=204,
)
async def delete_region(region_id: UUID = Path(...)):
    deleted = await region_service.delete(id=region_id)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Region not found")
