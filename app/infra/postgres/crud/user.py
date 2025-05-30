from app.infra.postgres.crud.base import CRUDBase
from app.infra.postgres.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    ...
    """
    Basic CRUD of the User model, inherits crud base methods
    """


crud_user = CRUDUser(model=User)
