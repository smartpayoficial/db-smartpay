from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Query, HTTPException, Path
from fastapi.responses import JSONResponse

from app.schemas.payment import PaymentCreate, PaymentUpdate, PaymentResponse
from app.infra.postgres.models.payment import Payment
from app.infra.postgres.crud.payment import crud_payment

router = APIRouter()

# --- Endpoints CRUD básicos para Payment ---

@router.post("", response_class=JSONResponse, response_model=PaymentResponse, status_code=201)
async def create_payment(new_payment: PaymentCreate):
    obj = await crud_payment.create(obj_in=new_payment)
    return obj

@router.get("", response_class=JSONResponse, status_code=200)
async def get_all_payments(
    plan_id: Optional[UUID] = Query(None),
    device_id: Optional[UUID] = Query(None),
    store_id: Optional[UUID] = Query(None, description="Filter payments by store_id of the user"),
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número de registros a devolver")
):
    import sys
    
    # Crear un diccionario de filtros
    filters = {}
    if plan_id:
        filters["plan_id"] = plan_id
    if device_id:
        filters["device_id"] = device_id
    
    try:
        # Create base query with prefetch related entities
        query = crud_payment.model.filter(**filters).prefetch_related(
            "plan", "plan__user", "plan__user__role", "plan__user__store",
            "plan__vendor", "plan__vendor__role", "plan__vendor__store",
            "device", "device__enrolment", "device__enrolment__user"
        )
        
        # If store_id is provided, filter payments where the plan's user belongs to the specified store
        if store_id:
            query = query.filter(plan__user__store_id=store_id)
            
        # Apply pagination
        payments = await query.offset(skip).limit(limit).all()
        
        payment_list = []
        for payment in payments:
            payment_dict = {
                "payment_id": str(payment.payment_id),
                "value": float(payment.value),
                "method": payment.method,
                "state": payment.state,
                "date": payment.date.isoformat(),
                "reference": payment.reference,
                "device_id": str(payment.device_id),
                "plan_id": str(payment.plan_id),
                "device": {
                    "device_id": str(payment.device.device_id),
                    "name": payment.device.name,
                    "imei": payment.device.imei,
                    "serial_number": payment.device.serial_number,
                    "model": payment.device.model,
                    "brand": payment.device.brand,
                    "product_name": payment.device.product_name,
                    "state": payment.device.state
                } if payment.device else None,
                "plan": {
                    "plan_id": str(payment.plan.plan_id),
                    "user": {
                        "user_id": str(payment.plan.user.user_id),
                        "first_name": payment.plan.user.first_name,
                        "middle_name": payment.plan.user.middle_name,
                        "last_name": payment.plan.user.last_name,
                        "second_last_name": payment.plan.user.second_last_name,
                        "email": payment.plan.user.email,
                        "role": payment.plan.user.role.name if payment.plan.user.role else None
                    } if payment.plan.user else None,
                    "vendor": {
                        "user_id": str(payment.plan.vendor.user_id),
                        "first_name": payment.plan.vendor.first_name,
                        "middle_name": payment.plan.vendor.middle_name,
                        "last_name": payment.plan.vendor.last_name,
                        "second_last_name": payment.plan.vendor.second_last_name,
                        "email": payment.plan.vendor.email,
                        "role": payment.plan.vendor.role.name if payment.plan.vendor.role else None
                    } if payment.plan.vendor else None
                } if payment.plan else None
            }
            payment_list.append(payment_dict)
        
        return payment_list
    except Exception as e:
        print(f"DEBUG: Error al obtener pagos: {str(e)}", file=sys.stderr)
        raise HTTPException(status_code=500, detail="Error retrieving payments")

@router.get("/{payment_id}", response_class=JSONResponse, response_model=PaymentResponse, status_code=200)
async def get_payment_by_id(payment_id: UUID = Path(...)):
    payment = await crud_payment.get_by_id(_id=payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@router.patch("/{payment_id}", response_class=JSONResponse, response_model=PaymentResponse, status_code=200)
async def update_payment(payment_id: UUID, payment_update: PaymentUpdate):
    # Verificamos si el pago existe antes de intentar actualizarlo
    payment_exists = await crud_payment.get_by_id(_id=payment_id)
    if not payment_exists:
        raise HTTPException(status_code=404, detail="Payment not found")
        
    # Verificamos si hay datos para actualizar
    update_data = payment_update.dict(exclude_unset=True)
    if not update_data:
        # Si no hay datos para actualizar, simplemente devolvemos el pago existente
        return payment_exists
        
    # Si hay datos para actualizar, procedemos con la actualización
    updated = await crud_payment.update(id=payment_id, obj_in=payment_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Payment not found")
        
    # Recupera el payment actualizado
    payment = await crud_payment.get_by_id(_id=payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found after update")
    return payment

@router.delete("/{payment_id}", status_code=204)
async def delete_payment(payment_id: UUID = Path(...)):
    deleted = await crud_payment.delete(id=payment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Payment not found")
    return None
