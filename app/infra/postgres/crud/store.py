from app.infra.postgres.crud.base import CRUDBase
from app.infra.postgres.models.store import Store
from app.schemas.store import StoreCreate, StoreUpdate


class CRUDStore(CRUDBase[Store, StoreCreate, StoreUpdate]):
    pass


crud_store = CRUDStore(model=Store)
