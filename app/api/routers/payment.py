from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Query, HTTPException, Path
from fastapi.responses import JSONResponse

from app.schemas.plan import PaymentCreate, PaymentUpdate, PaymentResponse
from app.infra.postgres.models.payment import Payment
from app.infra.postgres.crud.payment import crud_payment

router = APIRouter()

# --- Endpoints CRUD básicos para Payment ---

@router.post("", response_class=JSONResponse, response_model=PaymentResponse, status_code=201)
async def create_payment(new_payment: PaymentCreate):
    obj = await crud_payment.create(obj_in=new_payment)
    return obj

@router.get("", response_class=JSONResponse, response_model=List[PaymentResponse], status_code=200)
async def get_all_payments(plan_id: Optional[UUID] = Query(None)):
    payments = await crud_payment.get_all(plan_id=plan_id)
    return payments

@router.get("/{payment_id}", response_class=JSONResponse, response_model=PaymentResponse, status_code=200)
async def get_payment_by_id(payment_id: UUID = Path(...)):
    payment = await crud_payment.get_by_id(_id=payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@router.patch("/{payment_id}", response_class=JSONResponse, response_model=PaymentResponse, status_code=200)
async def update_payment(payment_id: UUID, payment_update: PaymentUpdate):
    updated = await crud_payment.update(_id=payment_id, obj_in=payment_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Payment not found")
    # Recupera el payment actualizado y adáptalo al esquema PaymentDB
    payment = await crud_payment.get_by_id(_id=payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found after update")
    return payment

@router.delete("/{payment_id}", status_code=204)
async def delete_payment(payment_id: UUID = Path(...)):
    deleted = await crud_payment.delete(_id=payment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Payment not found")
    return None
