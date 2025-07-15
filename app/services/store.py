from app.infra.postgres.crud.store import crud_store
from app.services.base import BaseService


class StoreService(BaseService):
    pass


store_service = StoreService(crud=crud_store)
