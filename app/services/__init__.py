from app.services.configuration import configuration_service
from app.services.device import device_service
from app.services.sim import sim_service
from app.services.television import television_service

# Re-export the services
configuration = configuration_service
device = device_service
sim = sim_service
television = television_service

__all__ = [
    "configuration",
    "device",
    "sim",
    "television",
]
