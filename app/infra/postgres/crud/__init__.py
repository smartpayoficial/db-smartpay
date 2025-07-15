from app.infra.postgres.crud.authentication import crud_authentication
from app.infra.postgres.crud.configuration import crud_configuration
from app.infra.postgres.crud.device import crud_device
from app.infra.postgres.crud.store import crud_store

# Re-export the CRUD modules
authentication = crud_authentication
configuration = crud_configuration
device = crud_device
store = crud_store

__all__ = [
    "authentication",
    "configuration",
    "device",
    "store",
]
