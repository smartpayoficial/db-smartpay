from app.infra.postgres.crud.base import CRUDBase
from app.infra.postgres.models.configuration import Configuration
from app.schemas.configuration import ConfigurationCreate, ConfigurationUpdate


class CRUDConfiguration(
    CRUDBase[Configuration, ConfigurationCreate, ConfigurationUpdate]
):
    pass


crud_configuration = CRUDConfiguration(model=Configuration)
