from typing import Any, Dict, List, Optional, Union

from fastapi.encoders import jsonable_encoder

from app.infra.postgres.models.sim import Sim
from app.schemas.sim import SimCreate, SimUpdate

from .base import CRUDBase


class CRUDSim(CRUDBase[Sim, SimCreate, SimUpdate]):
    async def get_by_number(self, number: str) -> Optional[Dict[str, Any]]:
        return await self.model.filter(number=number).values().first()

    async def get_by_device_id(
        self, device_id: str, *, skip: int = 0, limit: int = 100
    ) -> List[Dict[str, Any]]:
        return (
            await self.model.filter(device_id=device_id)
            .offset(skip)
            .limit(limit)
            .values()
        )

    async def get_by_icc_id(self, icc_id: str) -> Optional[Dict[str, Any]]:
        return await self.model.filter(icc_id=icc_id).values().first()

    async def create(self, *, obj_in: SimCreate) -> Dict[str, Any]:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        await db_obj.save()
        # Return the created object with all fields
        return await self.model.get(sim_id=db_obj.sim_id)

    async def update(  # type: ignore[override]
        self,
        *,
        _id: str,
        obj_in: Union[SimUpdate, Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        db_obj = await self.model.get_or_none(sim_id=_id)
        if not db_obj:
            return None

        update_data = (
            obj_in if isinstance(obj_in, dict) else obj_in.dict(exclude_unset=True)
        )

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        await db_obj.save()
        # Return the updated object with all fields
        return await self.model.filter(sim_id=_id).values().first()

    async def remove(self, sim_id: str) -> bool:
        obj = await self.model.get_or_none(sim_id=sim_id)
        if obj:
            await obj.delete()
            return True
        return False


sim = CRUDSim(model=Sim)
