from typing import List, Dict, Any, Optional
from uuid import UUID

from app.infra.postgres.crud.country import crud_country
from app.infra.postgres.crud.account_type import crud_account_type
from app.infra.postgres.models.country import Country
from app.services.base import BaseService


class CountryService(BaseService):
    async def get_all(self, *, skip: int = 0, limit: int = 100, payload: Optional[Dict[str, Any]] = None, **kwargs):
        """Override to ensure we get all countries"""
        import logging
        logger = logging.getLogger(__name__)
        
        # Get all countries directly from the model
        countries = await Country.all()
        logger.info(f"Retrieved {len(countries)} countries directly from Country model")
        
        # Apply filters if provided
        if payload and "name__icontains" in payload:
            name_filter = payload["name__icontains"].lower()
            countries = [c for c in countries if name_filter in c.name.lower()]
            logger.info(f"After filtering by name, {len(countries)} countries remain")
        
        return countries

    async def get_account_types_by_country(self, *, country_id: UUID, categories: Optional[List[str]] = None):
        return await crud_account_type.get_by_country_and_category(
            country_id=country_id, categories=categories
        )


country_service = CountryService(crud=crud_country)
