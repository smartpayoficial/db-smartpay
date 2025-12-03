from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Query

from app.schemas.account_type import AccountTypeDB, AccountCategoryEnum
from app.services.account_type import account_type_service

router = APIRouter()


@router.get(
    "/",
    response_model=List[AccountTypeDB],
    status_code=200,
    summary="Get Account Types",
)
async def get_all_account_types(
        country_id: Optional[UUID] = Query(
            None, description="Filter account types by country ID"
        ),
        categories: Optional[List[AccountCategoryEnum]] = Query(
            None, description="Filter account types by multiple categories"
        ),
    ):
    """
    Retrieves a list of account types.

    - If **country_id** is provided, it returns all account types available for that
      country (including international ones).
    - If **category** is provided, it filters account types by the specified category.
    - Both filters can be used simultaneously.
    """
    # Convert enums to their values for filtering
    category_values = [cat.value for cat in categories] if categories else None
    account_types = await account_type_service.get_account_types(
        country_id=country_id, categories=category_values
    )
    return account_types


@router.get(
    "/categories",
    response_model=List[str],
    summary="Get all account type categories"
)
async def get_account_type_categories():
    """
    Retrieves a list of all possible account type categories.
    """
    return [cat.value for cat in AccountCategoryEnum]
