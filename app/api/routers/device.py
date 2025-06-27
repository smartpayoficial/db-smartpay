from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import JSONResponse, Response

from app.schemas.device import DeviceCreate, DeviceDB, DeviceUpdate
from app.services.device import device_service

# Device Router
router = APIRouter()


@router.get(
    "/",
    response_class=JSONResponse,
    response_model=List[DeviceDB],
    status_code=200,
)
async def get_all_devices():
    devices = await device_service.get_all()
    return devices


@router.post(
    "/",
    response_class=JSONResponse,
    response_model=DeviceDB,
    status_code=201,
)
async def create_device(new_device: DeviceCreate):
    device = await device_service.create(obj_in=new_device)
    return device


@router.get(
    "/{device_id}",
    response_class=JSONResponse,
    response_model=DeviceDB,
    status_code=200,
)
async def get_device_by_id(device_id: UUID = Path(...)):
    device = await device_service.get_by_id(id=device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@router.patch(
    "/{device_id}",
    response_class=Response,
    status_code=204,
)
async def update_device(update_device: DeviceUpdate, device_id: UUID = Path(...)):
    await device_service.update(id=device_id, obj_in=update_device)


@router.delete(
    "/{device_id}",
    response_class=Response,
    status_code=204,
)
async def delete_device(device_id: UUID = Path(...)):
    deleted = await device_service.delete(id=device_id)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Device not found")
