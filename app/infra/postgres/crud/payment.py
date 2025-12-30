from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from app.infra.postgres.crud.base import CRUDBase
from app.infra.postgres.models.payment import Payment
from app.schemas.payment import PaymentCreate, PaymentUpdate

# Si tienes un PaymentUpdate, impórtalo aquí. Si no, puedes crear uno vacío o manejar solo PaymentCreate.
try:
    from app.schemas.payment import PaymentUpdate
except ImportError:
    PaymentUpdate = None  # O define una clase vacía si es necesario


class CRUDPayment(CRUDBase[Payment, PaymentCreate, PaymentUpdate]):
    async def create(self, *, obj_in: PaymentCreate) -> Payment:
        data = obj_in.dict()  # Pydantic v1 (si usas v2, ver opción C)
        d = data.get("date")
        if isinstance(d, datetime):
            # normaliza a ISO-8601; si viene naive, lo marco como UTC
            if d.tzinfo is None:
                d = d.replace(tzinfo=timezone.utc)
            data["date"] = d.isoformat()

        model = await self.model.create(**data)
        return await self.get_by_id(_id=model.payment_id)

    async def get_all(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        payload: Optional[dict] = None,
        plan_id: Optional[UUID] = None,
    ) -> List[Payment]:
        import logging

        logger = logging.getLogger(__name__)
        logger.info(
            f"CRUDPayment.get_all llamado con skip={skip}, limit={limit}, payload={payload}, plan_id={plan_id}"
        )

        query = self.model.all()

        if payload:
            if "plan_id" in payload and payload["plan_id"]:
                query = query.filter(plan_id=payload["plan_id"])
            if "device_id" in payload and payload["device_id"]:
                query = query.filter(device_id=payload["device_id"])
            if "television_id" in payload and payload["television_id"]:
                query = query.filter(television_id=payload["television_id"])
        elif plan_id:
            query = query.filter(plan_id=plan_id)

        query = query.offset(skip).limit(limit)

        try:
            results = await query.prefetch_related(
                "plan",
                "plan__user",
                "plan__user__role",
                "plan__vendor",
                "plan__vendor__role",
                "plan__device",
                "plan__television",
                "plan__payments",
                "device",
                "device__enrolment",
                "device__enrolment__user",
                "device__enrolment__user__role",
                "device__enrolment__vendor",
                "device__enrolment__vendor__role",
                "television",
                "television__enrolment",
                "television__enrolment__user",
                "television__enrolment__vendor",
            )
            # Ensure reverse relation 'plan.payments' is a concrete list for Pydantic
            try:
                for r in results:
                    if r.plan:
                        r.plan.payments = await r.plan.payments.all()
            except Exception:
                # If coercion fails, still return results; response building may handle it elsewhere
                pass
            return results
        except Exception as e:
            logger.error(f"Error al hacer prefetch_related: {str(e)}")
            return await query

    async def get_by_id(self, *, _id: UUID) -> Optional[Payment]:
        payment = (
            await self.model.filter(payment_id=_id)
            .prefetch_related(
                "plan",
                "plan__user",
                "plan__user__role",
                "plan__vendor",
                "plan__vendor__role",
                "plan__device",
                "plan__television",
                "plan__payments",
                "device",
                "television",
            )
            .first()
        )
        # Coerce plan.payments into a list for Pydantic serialization
        if payment and payment.plan:
            try:
                payment.plan.payments = await payment.plan.payments.all()
            except Exception:
                pass
        return payment


crud_payment = CRUDPayment(model=Payment)
