from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import JSONResponse, Response

from app.schemas.enrolment import EnrolmentCreate, EnrolmentDB, EnrolmentUpdate
from app.services.enrolment import enrolment_service

router = APIRouter()


@router.get(
    "/",  # Fix: Changed from "" to "/" to handle trailing slash
    response_class=JSONResponse,
    response_model=List[EnrolmentDB],
    status_code=200,
)
async def get_all_enrolments():
    """Get all enrolments"""
    enrolments = await enrolment_service.get_all()
    return enrolments


@router.post(
    "/", # Fix: Changed from "" to "/" to handle trailing slash
    response_class=JSONResponse,
    response_model=EnrolmentDB,
    status_code=201,
)
async def create_enrolment(new_enrolment: EnrolmentCreate):
    """Create a new enrolment"""
    enrolment = await enrolment_service.create(obj_in=new_enrolment)
    return enrolment


@router.get(
    "/{enrolment_id}",
    response_class=JSONResponse,
    response_model=EnrolmentDB,
    status_code=200,
)
async def get_enrolment_by_id(enrolment_id: UUID = Path(...)):
    """Get an enrolment by ID"""
    enrolment = await enrolment_service.get_by_id(id=enrolment_id)
    if enrolment is None:
        raise HTTPException(status_code=404, detail="Enrolment not found")
    return enrolment


@router.patch(
    "/{enrolment_id}",
    response_class=Response,
    status_code=204,
)
async def update_enrolment(
    update_enrolment: EnrolmentUpdate, enrolment_id: UUID = Path(...)
):
    """Update an enrolment"""
    await enrolment_service.update(id=enrolment_id, obj_in=update_enrolment)


@router.delete(
    "/{enrolment_id}",
    response_class=Response,
    status_code=204,
)
async def delete_enrolment(enrolment_id: UUID = Path(...)):
    """Delete an enrolment"""
    deleted = await enrolment_service.delete(id=enrolment_id)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Enrolment not found")
