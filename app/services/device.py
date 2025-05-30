from app.infra.postgres.crud.device import crud_device
from app.services.base import BaseService


class DeviceService(BaseService):
    pass


device_service = DeviceService(crud=crud_device)
