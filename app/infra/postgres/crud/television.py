from typing import Any, Dict, List, Optional

from app.infra.postgres.crud.base import CRUDBase
from app.infra.postgres.models.television import Television
from app.schemas.television import TelevisionCreate, TelevisionUpdate


class CRUDTelevision(CRUDBase[Television, TelevisionCreate, TelevisionUpdate]):
    async def get(self, *, id: Any) -> Optional[Television]:
        """
        Obtiene un dispositivo por su ID, con las relaciones 'enrolment' y 'actions' precargadas.
        """
        return (
            await self.model.filter(pk=id)
            .prefetch_related("enrolment")
            .first()
        )

    async def get_all(
        self,
        *,
        filters: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Television]:
        query = self.model.all().prefetch_related("enrolment__user")
        if filters:
            filters = filters.copy()
            if "enrolment_id" in filters:
                filters["enrolment__enrolment_id"] = filters.pop("enrolment_id")
            if "user_id" in filters:
                filters["enrolment__user__user_id"] = filters.pop("user_id")
            query = query.filter(**filters)
        results = await query.offset(skip).limit(limit)
        return results


crud_television = CRUDTelevision(model=Television)
