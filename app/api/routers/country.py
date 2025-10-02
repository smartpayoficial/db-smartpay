from typing import List, Optional
from uuid import UUID
import json
import os

from fastapi import APIRouter, HTTPException, Path, Query
from fastapi.responses import JSONResponse, Response

from app.schemas.country import CountryCreate, CountryDB, CountryUpdate
from app.schemas.account_type import AccountTypeInDB
from app.services.country import country_service
from app.infra.postgres.models.account_type import AccountCategoryEnum

router = APIRouter()

@router.get(
    "/all",
    response_class=JSONResponse,
    response_model=List[CountryDB],
    status_code=200,
)
async def get_all_countries_direct():
    """Get all countries directly from the database without any filtering or pagination"""
    from app.infra.postgres.models.country import Country
    
    # Query all countries directly from the model
    countries = await Country.all()
    
    # Convert to list of dictionaries for the response
    result = []
    for country in countries:
        result.append({
            "name": country.name,
            "code": country.code,
            "country_id": country.country_id,
            "phone_code": country.phone_code,
            "flag_icon_url": country.flag_icon_url
        })
    
    return result


@router.get(
    "/",
    response_class=JSONResponse,
    response_model=List[CountryDB],
    status_code=200,
)
async def get_all_countries(name: Optional[str] = Query(None, description="Filter countries by name (case-insensitive, partial match)")):
    import logging
    logger = logging.getLogger(__name__)
    
    filters = {}
    if name:
        filters["name__icontains"] = name
    
    countries = await country_service.get_all(payload=filters)
    logger.info(f"Retrieved {len(countries)} countries from database")
    
    # Ensure we're returning a list
    return list(countries)


@router.post(
    "/",
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
    country = await country_service.get(id=country_id)
    if country is None:
        raise HTTPException(status_code=404, detail="Country not found")
    return country

@router.get(
    "/{country_id}/account-types",
    response_class=JSONResponse,
    response_model=List[AccountTypeInDB],
    status_code=200,
)
async def get_country_account_types(
    country_id: UUID = Path(...),
    category: Optional[List[AccountCategoryEnum]] = Query(None, description="Filter account types by a list of categories")
):
    """Get all available account types for a given country, including international ones. Can be filtered by a list of categories."""
    # The service needs a list of string values from the enum list
    categories_str = [c.value for c in category] if category else None
    account_types = await country_service.get_account_types_by_country(
        country_id=country_id, categories=categories_str
    )
    return account_types


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
