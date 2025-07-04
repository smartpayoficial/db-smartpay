from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from fastapi import HTTPException, status
from tortoise.exceptions import IntegrityError

from app.infra.postgres.crud.sim import sim as crud_sim
from app.infra.postgres.models.sim import Sim
from app.schemas.sim import SimCreate, SimUpdate


class SimService:
    async def get(self, *, id: UUID) -> Optional[Sim]:
        return await crud_sim.get(id=id)

    async def get_by_number(self, *, number: str) -> Optional[Sim]:
        sims = await crud_sim.get_all(payload={"number": number}, limit=1)
        return sims[0] if sims else None

    async def get_by_device_id(
        self, *, device_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Sim]:
        return await crud_sim.get_all(
            payload={"device_id": device_id}, skip=skip, limit=limit
        )

    async def get_by_icc_id(self, *, icc_id: str) -> Optional[Sim]:
        sims = await crud_sim.get_all(payload={"icc_id": icc_id}, limit=1)
        return sims[0] if sims else None

    async def get_all(self, *, skip: int = 0, limit: int = 100) -> List[Sim]:
        return await crud_sim.get_all(skip=skip, limit=limit)

    async def create(self, *, obj_in: SimCreate) -> Sim:
        try:
            return await crud_sim.create(obj_in=obj_in)
        except IntegrityError as e:
            error_message = str(e).lower()
            if "duplicate key" in error_message or "unique constraint" in error_message:
                if "number" in error_message:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="A SIM card with this number already exists",
                    )
                elif "icc_id" in error_message:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="A SIM card with this ICC ID already exists",
                    )
            # Generic integrity error
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating SIM card: {e}",
            )

    async def update(
        self, *, id: UUID, obj_in: Union[SimUpdate, Dict[str, Any]]
    ) -> bool:
        # The update method in CRUDBase already checks for existence and returns a boolean
        updated = await crud_sim.update(id=id, obj_in=obj_in)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SIM card with ID {id} not found",
            )
        return updated

    async def remove(self, *, id: UUID) -> int:
        # The delete method in CRUDBase returns the count of deleted items
        deleted_count = await crud_sim.delete(id=id)
        if deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SIM card with ID {id} not found",
            )
        return deleted_count


sim_service = SimService()
