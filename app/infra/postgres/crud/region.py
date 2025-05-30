from app.infra.postgres.crud.base import CRUDBase
from app.infra.postgres.models.region import Region
from app.schemas.region import RegionCreate, RegionUpdate


class CRUDRegion(CRUDBase[Region, RegionCreate, RegionUpdate]):
    pass


crud_region = CRUDRegion(model=Region)
