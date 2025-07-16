from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Path, Query
from fastapi.responses import JSONResponse

from app.schemas.payment import PlanCreate, PlanUpdate, PlanDB, PlanResponse
from app.infra.postgres.crud.plan import crud_plan

router = APIRouter()

@router.post("", response_class=JSONResponse, response_model=PlanDB, status_code=201)
async def create_plan(new_plan: PlanCreate):
    obj = await crud_plan.create(obj_in=new_plan)
    return obj

@router.get("", response_class=JSONResponse, response_model=List[PlanResponse], status_code=200)
async def get_all_plans(
    device_id: Optional[UUID] = Query(None, description="Filter plans by device_id"),
    user_id: Optional[UUID] = Query(None, description="Filter plans by user_id")
):
    filters = {}
    if device_id:
        filters["device_id"] = device_id
    if user_id:
        filters["user_id"] = user_id
    
    # Define the related fields to prefetch
    prefetch_fields = [
        "user", "user__role", 
        "vendor", "vendor__role", 
        "device", "device__enrolment", 
        "device__enrolment__user", "device__enrolment__user__role",
        "device__enrolment__vendor", "device__enrolment__vendor__role"
    ]
    
    plans = await crud_plan.get_all(payload=filters, prefetch_fields=prefetch_fields)
    return plans

@router.get("/{plan_id}", response_class=JSONResponse, response_model=PlanResponse, status_code=200)
async def get_plan_by_id(plan_id: UUID = Path(...)):
    # Create a custom method in the CRUD class to get a plan with all related data
    plan = await crud_plan.model.filter(plan_id=plan_id).prefetch_related(
        "user", "user__role", 
        "vendor", "vendor__role", 
        "device", "device__enrolment", 
        "device__enrolment__user", "device__enrolment__user__role",
        "device__enrolment__vendor", "device__enrolment__vendor__role"
    ).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan

@router.patch("/{plan_id}", response_class=JSONResponse, response_model=PlanResponse, status_code=200)
async def update_plan(plan_id: UUID, plan_update: PlanUpdate):
    # Primero verificamos si el plan existe
    plan = await crud_plan.model.filter(plan_id=plan_id).prefetch_related(
        "user", "user__role", 
        "vendor", "vendor__role", 
        "device", "device__enrolment", 
        "device__enrolment__user", "device__enrolment__user__role",
        "device__enrolment__vendor", "device__enrolment__vendor__role"
    ).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    # Verificamos si hay datos para actualizar
    update_data = plan_update.dict(exclude_unset=True)
    if not update_data:
        # Si no hay datos para actualizar, simplemente devolvemos el plan sin modificar
        return plan
    
    # Si hay datos para actualizar, procedemos con la actualización
    updated = await crud_plan.update(id=plan_id, obj_in=plan_update)
    if not updated:
        # Esto no debería ocurrir ya que verificamos que el plan existe
        raise HTTPException(status_code=500, detail="Failed to update plan")
    
    # Recuperamos el plan actualizado con todas las relaciones
    updated_plan = await crud_plan.model.filter(plan_id=plan_id).prefetch_related(
        "user", "user__role", 
        "vendor", "vendor__role", 
        "device", "device__enrolment", 
        "device__enrolment__user", "device__enrolment__user__role",
        "device__enrolment__vendor", "device__enrolment__vendor__role"
    ).first()
    
    return updated_plan

@router.delete("/{plan_id}", status_code=204)
async def delete_plan(plan_id: UUID = Path(...)):
    deleted = await crud_plan.delete(id=plan_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Plan not found")
    return None
