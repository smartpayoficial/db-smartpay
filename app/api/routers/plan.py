from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Path, Query, status
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
    user_id: Optional[UUID] = Query(None, description="Filter plans by user_id"),
    store_id: Optional[UUID] = Query(None, description="Filter plans by store_id")
):
    import sys
    
    # Debug log for parameters
    if store_id:
        print(f"DEBUG: get_all_plans called with store_id={store_id}", file=sys.stderr)
    
    try:
        # Construir payload para el método get_all
        payload = {}
        if device_id:
            payload["device_id"] = device_id
        if user_id:
            payload["user_id"] = user_id
        
        # Definir campos a precargar
        prefetch_fields = [
            "user", "user__role", "user__store",
            "vendor", "vendor__role", "vendor__store",
            "device", "device__enrolment", 
            "device__enrolment__user", "device__enrolment__user__role",
            "device__enrolment__vendor", "device__enrolment__vendor__role"
        ]
        
        # Obtener todos los planes con los filtros básicos
        plans = await crud_plan.get_all(payload=payload, prefetch_fields=prefetch_fields)
        
        # Si se proporciona store_id, filtrar planes donde el usuario o vendedor pertenece a la tienda especificada
        if store_id:
            print(f"DEBUG: Filtering plans for store_id={store_id}", file=sys.stderr)
            filtered_plans = []
            for plan in plans:
                # Verificar si el plan tiene un usuario o vendedor asociado a la tienda
                if (plan.user and plan.user.store_id == store_id) or \
                   (plan.vendor and plan.vendor.store_id == store_id):
                    filtered_plans.append(plan)
            
            # Debug output
            print(f"DEBUG: Filtered - Found {len(filtered_plans)} plans for store_id={store_id}", file=sys.stderr)
            plans = filtered_plans
        
        return plans
    except Exception as e:
        print(f"ERROR: Exception in get_all_plans: {str(e)}", file=sys.stderr)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving plans: {str(e)}"
        )

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
