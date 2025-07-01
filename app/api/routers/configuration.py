from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import JSONResponse, Response

from app.schemas.configuration import (
    ConfigurationCreate,
    ConfigurationDB,
    ConfigurationUpdate,
)
from app.services.configuration import configuration_service

router = APIRouter()


@router.get(
    "/",
    response_class=JSONResponse,
    response_model=List[ConfigurationDB],
    status_code=200,
)
async def get_all_configurations():
    configurations = await configuration_service.get_all()
    return configurations


@router.post(
    "/",
    response_class=JSONResponse,
    response_model=ConfigurationDB,
    status_code=201,
)
async def create_configuration(new_configuration: ConfigurationCreate):
    configuration = await configuration_service.create(obj_in=new_configuration)
    return configuration


@router.get(
    "/{configuration_id}/",
    response_class=JSONResponse,
    response_model=ConfigurationDB,
    status_code=200,
)
async def get_configuration_by_id(configuration_id: UUID = Path(...)):
    configuration = await configuration_service.get_by_id(id=configuration_id)
    if configuration is None:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return configuration


@router.patch(
    "/{configuration_id}/",
    response_class=Response,
    status_code=204,
)
async def update_configuration(
    update_configuration: ConfigurationUpdate, configuration_id: UUID = Path(...)
):
    await configuration_service.update(id=configuration_id, obj_in=update_configuration)


@router.delete(
    "/{configuration_id}/",
    response_class=Response,
    status_code=204,
)
async def delete_configuration(configuration_id: UUID = Path(...)):
    deleted = await configuration_service.delete(id=configuration_id)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Configuration not found")
