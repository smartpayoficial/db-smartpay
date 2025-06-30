from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import JSONResponse, Response

from app.schemas.location import LocationCreate, LocationDB, LocationUpdate
from app.services.location import location_service

router = APIRouter()


@router.get(
    "/",
    response_class=JSONResponse,
    response_model=List[LocationDB],
    status_code=200,
)
async def get_all_locations(device_id: Optional[UUID] = None):
    payload = {}
    if device_id:
        payload["device_id"] = device_id
    locations = await location_service.get_all(payload=payload)
    return locations


@router.post(
    "/",
    response_class=JSONResponse,
    response_model=LocationDB,
    status_code=201,
)
async def create_location(new_location: LocationCreate):
    location = await location_service.create(obj_in=new_location)
    return location


@router.get(
    "/{location_id}",
    response_class=JSONResponse,
    response_model=LocationDB,
    status_code=200,
)
async def get_location_by_id(location_id: UUID = Path(...)):
    location = await location_service.get(id=location_id)
    if location is None:
        raise HTTPException(status_code=404, detail="Location not found")
    return location


@router.get(
    "/device/{device_id}",
    response_class=JSONResponse,
    response_model=LocationDB,
    status_code=200,
)
async def get_location_by_device_id(device_id: UUID = Path(...)):
    location = await location_service.get_last_by_device_id(device_id=device_id)
    if location is None:
        raise HTTPException(status_code=404, detail="Location not found")
    return location


@router.patch(
    "/{location_id}",
    response_class=Response,
    status_code=204,
)
async def update_location(
    update_location: LocationUpdate, location_id: UUID = Path(...)
):
    await location_service.update(id=location_id, obj_in=update_location)


@router.delete(
    "/{location_id}",
    response_class=Response,
    status_code=204,
)
async def delete_location(location_id: UUID = Path(...)):
    deleted = await location_service.delete(id=location_id)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Location not found")
