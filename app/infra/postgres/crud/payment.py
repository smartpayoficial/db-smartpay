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
        obj_in_data = obj_in.dict()
        model = await self.model.create(**obj_in_data)
        # Re-fetch with all relationships to ensure complete data in response
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

        # Intentar contar todos los pagos primero para verificar si hay datos
        total_count = await self.model.all().count()
        logger.info(f"Total de pagos en la base de datos: {total_count}")

        query = self.model.all()

        # Manejar filtros desde el parámetro payload
        if payload:
            logger.info(f"Aplicando filtros desde payload: {payload}")
            if "plan_id" in payload and payload["plan_id"]:
                logger.info(f"Filtrando por plan_id: {payload['plan_id']}")
                query = query.filter(plan_id=payload["plan_id"])
            if "device_id" in payload and payload["device_id"]:
                logger.info(f"Filtrando por device_id: {payload['device_id']}")
                query = query.filter(device_id=payload["device_id"])
        # Mantener compatibilidad con el parámetro plan_id directo
        elif plan_id:
            logger.info(f"Filtrando por plan_id directo: {plan_id}")
            query = query.filter(plan_id=plan_id)

        # Aplicar paginación
        query = query.offset(skip).limit(limit)

        # Obtener los resultados antes de aplicar prefetch_related para verificar
        results = await query
        logger.info(f"Número de resultados encontrados: {len(results)}")

        # Si no hay resultados, devolver lista vacía sin intentar prefetch_related
        if not results:
            logger.info("No se encontraron pagos, devolviendo lista vacía")
            return []

        try:
            # Intentar obtener los resultados con prefetch_related
            prefetched_results = await query.prefetch_related(
                "plan",
                "plan__user",
                "plan__user__role",
                "plan__vendor",
                "plan__vendor__role",
                "device",
                "device__enrolment",
                "device__enrolment__user",
                "device__enrolment__user__role",
                "device__enrolment__vendor",
                "device__enrolment__vendor__role",
            )
            logger.info(
                f"Número de resultados después de prefetch_related: {len(prefetched_results)}"
            )
            return prefetched_results
        except Exception as e:
            logger.error(f"Error al hacer prefetch_related: {str(e)}")
            # En caso de error con prefetch_related, devolver los resultados sin prefetch
            return results

    async def get_by_id(self, *, _id: UUID) -> Optional[Payment]:
        return (
            await self.model.filter(payment_id=_id)
            .prefetch_related(
                "plan",
                "plan__user",
                "plan__user__role",
                "plan__vendor",
                "plan__vendor__role",
                "plan__device",
            )
            .first()
        )


crud_payment = CRUDPayment(model=Payment)
