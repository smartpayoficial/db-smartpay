from app.infra.postgres.crud.role import crud_role
from app.services.base import BaseService


class RoleService(BaseService):
    pass


role_service = RoleService(crud=crud_role)
