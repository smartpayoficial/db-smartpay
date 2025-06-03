from app.infra.postgres.crud.user import crud_user
from app.services.base import BaseService


class UserService(BaseService):
    pass


user_service = UserService(crud=crud_user)
