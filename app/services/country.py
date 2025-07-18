from typing import List, Dict, Any, Optional

from app.infra.postgres.crud.country import crud_country
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


country_service = CountryService(crud=crud_country)
