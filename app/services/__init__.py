from app.services.authentication import authentication_service
from app.services.configuration import configuration_service
from app.services.device import device_service

# Re-export the services
authentication = authentication_service
configuration = configuration_service
device = device_service

__all__ = [
    "authentication",
    "configuration",
    "device",
]
