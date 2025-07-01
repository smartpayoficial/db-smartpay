from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import JSONResponse

from app.infra.postgres.models.factory_reset_protection import (
    FactoryResetProtectionState,
)
from app.schemas.factory_reset_protection import (
    FactoryResetProtectionCreate,
    FactoryResetProtectionResponse,
    FactoryResetProtectionUpdate,
)
from app.services.factory_reset_protection import factory_reset_protection_service

router = APIRouter()


@router.get(
    "", response_model=List[FactoryResetProtectionResponse], response_class=JSONResponse
)
async def get_all_factory_protections(
    state: Optional[FactoryResetProtectionState] = None,
):
    payload = {}
    if state:
        payload["state"] = state

    return await factory_reset_protection_service.get_all(filters=payload)


@router.post(
    "",
    response_model=FactoryResetProtectionResponse,
    response_class=JSONResponse,
    status_code=201,
)
async def create_factory_protection(new_factory_reset: FactoryResetProtectionCreate):
    return await factory_reset_protection_service.create(obj_in=new_factory_reset)


@router.get(
    "/{factory_reset_protection_id}",
    response_model=FactoryResetProtectionResponse,
    response_class=JSONResponse,
)
async def get_factory_reset_by_id(factory_reset_protection_id: UUID = Path(...)):
    factoryReset = await factory_reset_protection_service.get_by_id(
        id=factory_reset_protection_id
    )
    if not factoryReset:
        raise HTTPException(
            status_code=404, detail="Factory reset protection not found"
        )
    return factoryReset


@router.get(
    "/accountId/{account_id}",
    response_model=FactoryResetProtectionResponse,
    response_class=JSONResponse,
)
async def get_factory_reset_by_account_id(account_id: str = Path(...)):
    factoryReset = (
        await factory_reset_protection_service.get_factory_reset_by_account_id(
            id=account_id
        )
    )
    if not factoryReset:
        raise HTTPException(
            status_code=404, detail="Factory reset protection not found"
        )
    return factoryReset


@router.patch(
    "/{factory_reset_protection_id}",
    response_model=FactoryResetProtectionResponse,
    response_class=JSONResponse,
)
async def update_factory_reset_protection(
    factory_reset_protection_id: UUID, update: FactoryResetProtectionUpdate
):
    was_updated = await factory_reset_protection_service.update(
        id=factory_reset_protection_id, obj_in=update
    )
    if not was_updated:
        raise HTTPException(
            status_code=404, detail="Factory reset protection not found"
        )

    updated = await factory_reset_protection_service.get_by_id(
        id=factory_reset_protection_id
    )

    if not updated:
        raise HTTPException(
            status_code=404, detail="Factory reset protection not found after update"
        )

    return updated


@router.delete("/{factory_reset_protection_id}", response_class=JSONResponse)
async def delete_factory_reset_protection(factory_reset_protection_id: UUID):
    deleted = await factory_reset_protection_service.delete(
        id=factory_reset_protection_id
    )
    if not deleted:
        raise HTTPException(
            status_code=404, detail="Factory reset protection not found"
        )
    return {"deleted": True}
