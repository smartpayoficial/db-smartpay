from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import JSONResponse

from app.schemas.payment import PaymentCreate, PaymentBase, PaymentUpdate, PaymentDB
from app.infra.postgres.models.payment import Payment
from app.infra.postgres.crud.payment import crud_payment

router = APIRouter()

# --- Endpoints CRUD básicos para Payment ---

@router.post("", response_class=JSONResponse, response_model=PaymentDB, status_code=201)
async def create_payment(new_payment: PaymentCreate):
    obj = await crud_payment.create(obj_in=new_payment)
    return obj

@router.get("", response_class=JSONResponse, response_model=List[PaymentDB], status_code=200)
async def get_all_payments():
    payments = await crud_payment.get_all()
    return payments

@router.get("/{payment_id}", response_class=JSONResponse, response_model=PaymentDB, status_code=200)
async def get_payment_by_id(payment_id: UUID = Path(...)):
    payment = await crud_payment.get(id=payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@router.patch("/{payment_id}", response_class=JSONResponse, response_model=PaymentDB, status_code=200)
async def update_payment(payment_id: UUID, payment_update: PaymentUpdate):
    updated = await crud_payment.update(id=payment_id, obj_in=payment_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Payment not found")
    return updated

@router.delete("/{payment_id}", status_code=204)
async def delete_payment(payment_id: UUID = Path(...)):
    deleted = await crud_payment.remove(id=payment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Payment not found")
    return None
