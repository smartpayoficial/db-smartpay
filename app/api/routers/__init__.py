from app.api.routers.authentication import router as authentication_router
from app.api.routers.configuration import router as configuration_router
from app.api.routers.device import router as device_router

# Re-export the routers
router = authentication_router
configuration = configuration_router
device = device_router

__all__ = [
    "router",
    "configuration",
    "device",
]
