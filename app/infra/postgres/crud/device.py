from typing import Any, Dict, List, Optional

from app.infra.postgres.crud.base import CRUDBase
from app.infra.postgres.models.device import Device
from app.schemas.device import DeviceCreate, DeviceUpdate


class CRUDDevice(CRUDBase[Device, DeviceCreate, DeviceUpdate]):
    async def get_all(
        self, *, skip: int = 0, limit: int = 100, filters: Optional[Dict[str, Any]] = None
    ) -> List[Device]:
        query = self.model.all()
        if filters and "enrolment_id" in filters:
            query = query.filter(enrolment_id=filters["enrolment_id"])
        return await query.offset(skip).limit(limit)


crud_device = CRUDDevice(model=Device)
