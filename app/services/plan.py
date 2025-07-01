from app.infra.postgres.crud.plan import crud_plan
from app.services.base import BaseService


class PlanService(BaseService):
    pass


plan_service = PlanService(crud=crud_plan)
