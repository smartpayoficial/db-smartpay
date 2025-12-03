from typing import Any, Dict, Optional

from fastapi import HTTPException, status
from tortoise.exceptions import IntegrityError

from app.infra.postgres.crud.television import crud_television
from app.infra.postgres.models.television import Television
from app.schemas.television import TelevisionCreate, TelevisionUpdate
from app.services.base import BaseService


class TelevisionService(BaseService[Television, TelevisionCreate, TelevisionUpdate]):
    async def create(self, *, obj_in: TelevisionCreate) -> Television:
        try:
            return await self.crud.create(obj_in=obj_in)
        except IntegrityError as e:
            error_message = str(e).lower()
            if "duplicate key" in error_message or "unique constraint" in error_message:
                if "serial_number_key" in error_message:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="A device with this Serial already exists.",
                    )
            # For other integrity errors, we can be more generic
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Database integrity error: {e}",
            )

    async def count(self) -> int:
        """
        Count the total number of devices in the system.

        Returns:
            int: The total count of devices
        """
        return await self.crud.count(payload={})


television_service = TelevisionService(crud_television)
