from typing import List
from uuid import UUID

from fastapi import APIRouter, Body, HTTPException, Path, Query, Response, status
from fastapi.responses import JSONResponse

from app.schemas.sim import Sim, SimCreate, SimUpdate
from app.services import sim_service

router = APIRouter()


@router.get(
    "",
    response_class=JSONResponse,
    response_model=List[Sim],
    status_code=status.HTTP_200_OK,
    summary="Get all SIM cards",
    description="Retrieve a list of all SIM cards with pagination.",
)
async def get_all_sims(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
):
    return await sim_service.get_all(skip=skip, limit=limit)


@router.get(
    "/by-device/{device_id}",
    response_class=JSONResponse,
    response_model=List[Sim],
    status_code=status.HTTP_200_OK,
    summary="Get SIM cards by device ID",
    description="Retrieve all SIM cards associated with a specific device.",
)
async def get_sims_by_device(
    device_id: UUID = Path(..., description="The ID of the device"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
):
    return await sim_service.get_by_device_id(
        device_id=str(device_id), skip=skip, limit=limit
    )


@router.get(
    "/{sim_id}",
    response_class=JSONResponse,
    response_model=Sim,
    status_code=status.HTTP_200_OK,
    summary="Get SIM card by ID",
    description="Retrieve a specific SIM card by its ID.",
)
async def get_sim(sim_id: UUID = Path(..., description="The ID of the SIM card")):
    sim_card = await sim_service.get(id=str(sim_id))
    if not sim_card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SIM card with ID {sim_id} not found",
        )
    return sim_card


@router.get(
    "/number/{number}",
    response_class=JSONResponse,
    response_model=Sim,
    status_code=status.HTTP_200_OK,
    summary="Get SIM card by number",
    description="Retrieve a specific SIM card by its phone number.",
)
async def get_sim_by_number(
    number: str = Path(..., description="The phone number of the SIM card")
):
    sim_card = await sim_service.get_by_number(number=number)
    if not sim_card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SIM card with number {number} not found",
        )
    return sim_card


@router.post(
    "",
    response_class=JSONResponse,
    response_model=Sim,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new SIM card",
    description="Create a new SIM card with the provided details.",
)
async def create_sim(sim_card: SimCreate):
    return await sim_service.create(obj_in=sim_card)


@router.patch(
    "/{sim_id}",
    response_class=JSONResponse,
    response_model=Sim,
    status_code=status.HTTP_200_OK,
    summary="Update a SIM card",
    description="Update an existing SIM card's details.",
)
async def update_sim(
    sim_id: UUID = Path(..., description="The ID of the SIM card to update"),
    sim_card_in: SimUpdate = Body(...),
):
    return await sim_service.update(sim_id=str(sim_id), obj_in=sim_card_in)


@router.delete(
    "/{sim_id}",
    response_class=Response,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a SIM card",
    description="Delete a SIM card by its ID.",
)
async def delete_sim(
    sim_id: UUID = Path(..., description="The ID of the SIM card to delete")
):
    await sim_service.remove(sim_id=str(sim_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
