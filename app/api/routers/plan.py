from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import JSONResponse

from app.schemas.payment import PlanCreate, PlanUpdate, PlanDB
from app.infra.postgres.crud.plan import crud_plan

router = APIRouter()

@router.post("", response_class=JSONResponse, response_model=PlanDB, status_code=201)
async def create_plan(new_plan: PlanCreate):
    obj = await crud_plan.create(obj_in=new_plan)
    return obj

@router.get("", response_class=JSONResponse, response_model=List[PlanDB], status_code=200)
async def get_all_plans():
    plans = await crud_plan.get_multi()
    return plans

@router.get("/{plan_id}", response_class=JSONResponse, response_model=PlanDB, status_code=200)
async def get_plan_by_id(plan_id: UUID = Path(...)):
    plan = await crud_plan.get(id=plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan

@router.patch("/{plan_id}", response_class=JSONResponse, response_model=PlanDB, status_code=200)
async def update_plan(plan_id: UUID, plan_update: PlanUpdate):
    updated = await crud_plan.update(id=plan_id, obj_in=plan_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Plan not found")
    return updated

@router.delete("/{plan_id}", status_code=204)
async def delete_plan(plan_id: UUID = Path(...)):
    deleted = await crud_plan.remove(id=plan_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Plan not found")
    return None
