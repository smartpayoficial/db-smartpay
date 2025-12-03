from typing import Any, Dict, List, Optional

from app.infra.postgres.crud.base import CRUDBase
from app.infra.postgres.models.action import Action
from app.schemas.action import ActionCreate, ActionUpdate


class CRUDAction(CRUDBase[Action, ActionCreate, ActionUpdate]):
    async def get_all(
        self, *, skip: int = 0, limit: int = 100, filters: Optional[Dict[str, Any]] = None, prefetch_fields: Optional[List[str]] = None, order_by: Optional[List[str]] = None
    ) -> List[Action]:
        query = self.model.all()
        if prefetch_fields:
            query = query.prefetch_related(*prefetch_fields)
        if filters:
            query = query.filter(**filters)

        # Apply ordering
        if order_by:
            query = query.order_by(*order_by)
        elif hasattr(self.model, "created_at"):
            query = query.order_by("-created_at")
        elif hasattr(self.model, "initial_date"):
            query = query.order_by("-initial_date")

        return await query.offset(skip).limit(limit).all()


crud_action = CRUDAction(model=Action)
