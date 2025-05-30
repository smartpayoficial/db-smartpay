from app.infra.postgres.crud.base import CRUDBase
from app.infra.postgres.models.authentication import Authentication
from app.schemas.authentication import AuthenticationCreate, AuthenticationUpdate


class CRUDAuthentication(
    CRUDBase[Authentication, AuthenticationCreate, AuthenticationUpdate]
):
    pass


crud_authentication = CRUDAuthentication(model=Authentication)
