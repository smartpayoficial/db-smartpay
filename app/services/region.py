from app.infra.postgres.crud.region import crud_region
from app.services.base import BaseService


class RegionService(BaseService):
    pass


region_service = RegionService(crud=crud_region)
