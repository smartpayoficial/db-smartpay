from app.infra.postgres.crud.user import crud_user
from app.services.base import BaseService


class ServiceUsers(BaseService): ...


user_service = ServiceUsers(crud=crud_user)
