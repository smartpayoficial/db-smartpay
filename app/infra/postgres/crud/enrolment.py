from app.infra.postgres.crud.base import CRUDBase
from app.infra.postgres.models.enrolment import Enrolment
from app.schemas.enrolment import EnrolmentCreate, EnrolmentUpdate


class CRUDEnrolment(CRUDBase[Enrolment, EnrolmentCreate, EnrolmentUpdate]):
    pass


crud_enrolment = CRUDEnrolment(model=Enrolment)
