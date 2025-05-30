from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import JSONResponse, Response

from app.schemas.location import (
    CityCreate,
    CityDB,
    CityUpdate,
    CountryCreate,
    CountryDB,
    CountryUpdate,
    RegionCreate,
    RegionDB,
    RegionUpdate,
)
from app.services.location import city_service, country_service, region_service

# Country Router
router_country = APIRouter()


@router_country.get(
    "",
    response_class=JSONResponse,
    response_model=List[CountryDB],
    status_code=200,
)
async def get_all_countries():
    countries = await country_service.get_all()
    return countries


@router_country.post(
    "",
    response_class=JSONResponse,
    response_model=CountryDB,
    status_code=201,
)
async def create_country(new_country: CountryCreate):
    country = await country_service.create(obj_in=new_country)
    return country


@router_country.get(
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


@router_country.patch(
    "/{country_id}",
    response_class=Response,
    status_code=204,
)
async def update_country(update_country: CountryUpdate, country_id: UUID = Path(...)):
    await country_service.update(id=country_id, obj_in=update_country)


@router_country.delete(
    "/{country_id}",
    response_class=Response,
    status_code=204,
)
async def delete_country(country_id: UUID = Path(...)):
    deleted = await country_service.delete(id=country_id)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Country not found")


# Region Router
router_region = APIRouter()


@router_region.get(
    "",
    response_class=JSONResponse,
    response_model=List[RegionDB],
    status_code=200,
)
async def get_all_regions():
    regions = await region_service.get_all()
    return regions


@router_region.post(
    "",
    response_class=JSONResponse,
    response_model=RegionDB,
    status_code=201,
)
async def create_region(new_region: RegionCreate):
    region = await region_service.create(obj_in=new_region)
    return region


@router_region.get(
    "/{region_id}",
    response_class=JSONResponse,
    response_model=RegionDB,
    status_code=200,
)
async def get_region_by_id(region_id: UUID = Path(...)):
    region = await region_service.get_by_id(id=region_id)
    if region is None:
        raise HTTPException(status_code=404, detail="Region not found")
    return region


@router_region.patch(
    "/{region_id}",
    response_class=Response,
    status_code=204,
)
async def update_region(update_region: RegionUpdate, region_id: UUID = Path(...)):
    await region_service.update(id=region_id, obj_in=update_region)


@router_region.delete(
    "/{region_id}",
    response_class=Response,
    status_code=204,
)
async def delete_region(region_id: UUID = Path(...)):
    deleted = await region_service.delete(id=region_id)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Region not found")


# City Router
router_city = APIRouter()


@router_city.get(
    "",
    response_class=JSONResponse,
    response_model=List[CityDB],
    status_code=200,
)
async def get_all_cities():
    cities = await city_service.get_all()
    return cities


@router_city.post(
    "",
    response_class=JSONResponse,
    response_model=CityDB,
    status_code=201,
)
async def create_city(new_city: CityCreate):
    city = await city_service.create(obj_in=new_city)
    return city


@router_city.get(
    "/{city_id}",
    response_class=JSONResponse,
    response_model=CityDB,
    status_code=200,
)
async def get_city_by_id(city_id: UUID = Path(...)):
    city = await city_service.get_by_id(id=city_id)
    if city is None:
        raise HTTPException(status_code=404, detail="City not found")
    return city


@router_city.patch(
    "/{city_id}",
    response_class=Response,
    status_code=204,
)
async def update_city(update_city: CityUpdate, city_id: UUID = Path(...)):
    await city_service.update(id=city_id, obj_in=update_city)


@router_city.delete(
    "/{city_id}",
    response_class=Response,
    status_code=204,
)
async def delete_city(city_id: UUID = Path(...)):
    deleted = await city_service.delete(id=city_id)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="City not found")
