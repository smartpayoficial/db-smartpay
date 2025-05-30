from app.infra.postgres.crud.base import CRUDBase
from app.infra.postgres.models.role import Role
from app.schemas.role import RoleCreate, RoleUpdate


class CRUDRole(CRUDBase[Role, RoleCreate, RoleUpdate]):
    pass


crud_role = CRUDRole(model=Role)
