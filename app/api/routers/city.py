from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Path, Query
from fastapi.responses import JSONResponse, Response

from app.schemas.city import CityCreate, CityDB, CityUpdate
from app.services.city import city_service

router = APIRouter()


@router.get(
    "/",
    response_class=JSONResponse,
    response_model=List[CityDB],
    status_code=200,
)
async def get_all_cities(
    name: Optional[str] = Query(None, description="Filter cities by name (case-insensitive, partial match)"),
    region_id: Optional[UUID] = Query(None, description="Filter cities by region ID")
):
    filters = {}
    if name:
        filters["name__icontains"] = name
    if region_id:
        filters["region_id"] = region_id
    
    cities = await city_service.get_all(payload=filters)
    return cities


@router.post(
    "/",
    response_class=JSONResponse,
    response_model=CityDB,
    status_code=201,
)
async def create_city(new_city: CityCreate):
    city = await city_service.create(obj_in=new_city)
    return city


@router.get(
    "/{city_id}",
    response_class=JSONResponse,
    response_model=CityDB,
    status_code=200,
)
async def get_city_by_id(city_id: UUID = Path(...)):
    city = await city_service.get(id=city_id)
    if city is None:
        raise HTTPException(status_code=404, detail="City not found")
    return city


@router.patch(
    "/{city_id}",
    response_class=Response,
    status_code=204,
)
async def update_city(update_city: CityUpdate, city_id: UUID = Path(...)):
    await city_service.update(id=city_id, obj_in=update_city)


@router.delete(
    "/{city_id}",
    response_class=Response,
    status_code=204,
)
async def delete_city(city_id: UUID = Path(...)):
    deleted = await city_service.delete(id=city_id)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="City not found")
