from app.infra.postgres.crud.base import CRUDBase
from app.infra.postgres.models.device import Device
from app.schemas.device import DeviceCreate, DeviceUpdate


class CRUDDevice(CRUDBase[Device, DeviceCreate, DeviceUpdate]):
    pass


crud_device = CRUDDevice(model=Device)
