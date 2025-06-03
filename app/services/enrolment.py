from app.infra.postgres.crud.enrolment import crud_enrolment
from app.services.base import BaseService


class EnrolmentService(BaseService):
    pass


enrolment_service = EnrolmentService(crud=crud_enrolment)
