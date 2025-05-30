from app.infra.postgres.crud.base import CRUDBase
from app.infra.postgres.models.auth import Authentication, Configuration, Role
from app.schemas.auth import (
    AuthenticationCreate,
    AuthenticationUpdate,
    ConfigurationCreate,
    ConfigurationUpdate,
    RoleCreate,
    RoleUpdate,
)


class CRUDRole(CRUDBase[Role, RoleCreate, RoleUpdate]):
    pass


class CRUDConfiguration(
    CRUDBase[Configuration, ConfigurationCreate, ConfigurationUpdate]
):
    pass


class CRUDAuthentication(
    CRUDBase[Authentication, AuthenticationCreate, AuthenticationUpdate]
):
    pass


role_crud = CRUDRole(model=Role)
config_crud = CRUDConfiguration(model=Configuration)
auth_crud = CRUDAuthentication(model=Authentication)
