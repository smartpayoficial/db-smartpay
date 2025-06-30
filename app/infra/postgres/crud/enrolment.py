from typing import Any, Optional

from app.infra.postgres.crud.base import CRUDBase
from app.infra.postgres.models.enrolment import Enrolment
from app.schemas.enrolment import EnrolmentCreate, EnrolmentUpdate


class CRUDEnrolment(CRUDBase[Enrolment, EnrolmentCreate, EnrolmentUpdate]):
    async def get(self, *, id: Any) -> Optional[Enrolment]:
        return await self.model.filter(pk=id).first()


crud_enrolment = CRUDEnrolment(model=Enrolment)
