from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import JSONResponse, Response

from app.schemas.country import CountryCreate, CountryDB, CountryUpdate
from app.services.country import country_service

router = APIRouter()


@router.get(
    "",
    response_class=JSONResponse,
    response_model=List[CountryDB],
    status_code=200,
)
async def get_all_countries():
    countries = await country_service.get_all()
    return countries


@router.post(
    "",
    response_class=JSONResponse,
    response_model=CountryDB,
    status_code=201,
)
async def create_country(new_country: CountryCreate):
    country = await country_service.create(obj_in=new_country)
    return country


@router.get(
    "/{country_id}",
    response_class=JSONResponse,
    response_model=CountryDB,
    status_code=200,
)
async def get_country_by_id(country_id: UUID = Path(...)):
    country = await country_service.get_by_id(id=country_id)
    if country is None:
        raise HTTPException(status_code=404, detail="Country not found")
    return country


@router.patch(
    "/{country_id}",
    response_class=Response,
    status_code=204,
)
async def update_country(update_country: CountryUpdate, country_id: UUID = Path(...)):
    await country_service.update(id=country_id, obj_in=update_country)


@router.delete(
    "/{country_id}",
    response_class=Response,
    status_code=204,
)
async def delete_country(country_id: UUID = Path(...)):
    deleted = await country_service.delete(id=country_id)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Country not found")
