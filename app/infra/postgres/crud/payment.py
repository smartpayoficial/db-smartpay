from typing import List, Optional
from uuid import UUID

from app.infra.postgres.crud.base import CRUDBase
from app.infra.postgres.models.payment import Payment
from app.schemas.plan import PaymentCreate, PaymentUpdate

class CRUDPayment(CRUDBase[Payment, PaymentCreate, PaymentUpdate]):
    async def create(self, *, obj_in: PaymentCreate) -> Payment:
        obj_in_data = obj_in.dict()
        model = await self.model.create(**obj_in_data)
        # Re-fetch to load relationships
        return await self.get_by_id(_id=model.payment_id)
    async def get_all(self, *, plan_id: Optional[UUID] = None) -> List[Payment]:
        query = self.model.all()
        if plan_id:
            query = query.filter(plan_id=plan_id)
        
        return await query.prefetch_related(
            "plan", "plan__user", "plan__user__role", "plan__vendor", "plan__vendor__role",
            "device", "device__enrolment", "device__enrolment__user", "device__enrolment__user__role",
            "device__enrolment__vendor", "device__enrolment__vendor__role"
        )

    async def get_by_id(self, *, _id: UUID) -> Optional[Payment]:
        return await self.model.filter(payment_id=_id).prefetch_related(
            "plan", "plan__user", "plan__user__role", "plan__vendor", "plan__vendor__role",
            "device", "device__enrolment", "device__enrolment__user", "device__enrolment__user__role",
            "device__enrolment__vendor", "device__enrolment__vendor__role"
        ).first()

crud_payment = CRUDPayment(model=Payment)
