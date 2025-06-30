from typing import Any, Dict, List, Optional

from app.infra.postgres.crud.base import CRUDBase
from app.infra.postgres.models.action import Action
from app.schemas.action import ActionCreate, ActionUpdate


class CRUDAction(CRUDBase[Action, ActionCreate, ActionUpdate]):
    async def get_all(
        self, *, skip: int = 0, limit: int = 100, filters: Optional[Dict[str, Any]] = None
    ) -> List[Action]:
        query = self.model.all().prefetch_related("applied_by__role")
        if filters:
            query = query.filter(**filters)
        return await query.offset(skip).limit(limit)


crud_action = CRUDAction(model=Action)
