from typing import Any, Dict, List, Optional, Union

from fastapi import HTTPException, status
from tortoise.exceptions import IntegrityError

from app.infra.postgres.crud.sim import sim as crud_sim
from app.schemas.sim import SimCreate, SimUpdate


class SimService:
    async def get_by_id(self, sim_id: str) -> Optional[Dict[str, Any]]:
        return await crud_sim.get_by_id(_id=sim_id)

    async def get_by_number(self, number: str) -> Optional[Dict[str, Any]]:
        return await crud_sim.get_by_number(number=number)

    async def get_by_device_id(
        self, device_id: str, *, skip: int = 0, limit: int = 100
    ) -> List[Dict[str, Any]]:
        return await crud_sim.get_by_device_id(
            device_id=device_id, skip=skip, limit=limit
        )

    async def get_by_icc_id(self, icc_id: str) -> Optional[Dict[str, Any]]:
        return await crud_sim.get_by_icc_id(icc_id=icc_id)

    async def get_all(self, *, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        return await crud_sim.get_all(skip=skip, limit=limit)

    async def create(self, obj_in: SimCreate) -> Dict[str, Any]:
        try:
            return await crud_sim.create(obj_in=obj_in)
        except IntegrityError as e:
            if "duplicate key" in str(e).lower():
                if "number" in str(e):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="A SIM card with this number already exists",
                    )
                elif "icc_id" in str(e):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="A SIM card with this ICC ID already exists",
                    )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating SIM card",
            )

    async def update(
        self, sim_id: str, obj_in: Union[SimUpdate, Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        sim_card = await self.get_by_id(sim_id=sim_id)
        if not sim_card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SIM card with ID {sim_id} not found",
            )

        try:
            return await crud_sim.update(_id=sim_id, obj_in=obj_in)
        except IntegrityError as e:
            if "duplicate key" in str(e).lower():
                if "number" in str(e):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="A SIM card with this number already exists",
                    )
                elif "icc_id" in str(e):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="A SIM card with this ICC ID already exists",
                    )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error updating SIM card",
            )

    async def remove(self, sim_id: str) -> bool:
        sim_card = await self.get_by_id(sim_id=sim_id)
        if not sim_card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SIM card with ID {sim_id} not found",
            )
        return await crud_sim.remove(sim_id=sim_id)


sim_service = SimService()
