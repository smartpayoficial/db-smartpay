from app.infra.postgres.crud.authentication import crud_authentication
from app.services.base import BaseService


class AuthenticationService(BaseService):
    pass


authentication_service = AuthenticationService(crud=crud_authentication)
