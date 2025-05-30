from app.infra.postgres.crud.configuration import crud_configuration
from app.services.base import BaseService


class ConfigurationService(BaseService):
    pass


configuration_service = ConfigurationService(crud=crud_configuration)
