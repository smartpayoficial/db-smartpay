from app.infra.postgres.crud.base import CRUDBase
from app.infra.postgres.models.payment import Plan
from app.schemas.payment import PlanCreate, PlanUpdate

class CRUDPlan(CRUDBase[Plan, PlanCreate, PlanUpdate]):
    pass

crud_plan = CRUDPlan(model=Plan)
