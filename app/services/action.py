from app.infra.postgres.crud.action import crud_action
from app.infra.postgres.models.action import Action
from app.schemas.action import ActionCreate, ActionUpdate
from app.services.base import BaseService


class ActionService(BaseService[Action, ActionCreate, ActionUpdate]):
    pass


action_service = ActionService(crud_action)
