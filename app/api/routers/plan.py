from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import JSONResponse

from app.schemas.plan import PlanCreate, PlanUpdate, PlanDB
from app.services.plan import plan_service

router = APIRouter()

@router.post("", response_class=JSONResponse, response_model=PlanDB, status_code=201)
async def create_plan(new_plan: PlanCreate):
    obj = await plan_service.create(obj_in=new_plan)
    return obj

@router.get("", response_class=JSONResponse, response_model=List[PlanDB], status_code=200)
async def get_all_plans():
    plans = await plan_service.get_all()
    return plans

@router.get("/{plan_id}", response_class=JSONResponse, response_model=PlanDB, status_code=200)
async def get_plan_by_id(plan_id: UUID = Path(...)):
    plan = await plan_service.get(id=plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan

@router.patch("/{plan_id}", response_class=JSONResponse, response_model=PlanDB, status_code=200)
async def update_plan(plan_id: UUID, plan_update: PlanUpdate):
    plan = await plan_service.update(id=plan_id, obj_in=plan_update)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan

@router.delete("/{plan_id}", status_code=204)
async def delete_plan(plan_id: UUID = Path(...)):
    plan = await plan_service.get(id=plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    await plan_service.delete(id=plan_id)
    return Response(status_code=204)
