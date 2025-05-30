from app.infra.postgres.crud.auth import auth_crud, config_crud, role_crud
from app.services.base import BaseService


class RoleService(BaseService):
    pass


class ConfigurationService(BaseService):
    pass


class AuthenticationService(BaseService):
    pass


role_service = RoleService(crud=role_crud)
config_service = ConfigurationService(crud=config_crud)
auth_service = AuthenticationService(crud=auth_crud)
