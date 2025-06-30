from app.infra.postgres.crud.device import crud_device
from app.infra.postgres.models.device import Device
from app.schemas.device import DeviceCreate, DeviceUpdate
from app.services.base import BaseService


class DeviceService(BaseService):
    pass


class DeviceService(BaseService[Device, DeviceCreate, DeviceUpdate]):
    pass


device_service = DeviceService(crud_device)
