from .action import router as action_router
from .analytics import router as analytics_router
from .authentication import router as auth_router
from .city import router as city_router
from .configuration import router as configuration_router
from .country import router as country_router
from .device import router as device_router
from .enrolment import router as enrolment_router
from .factory_reset_protection import router as factory_reset_protection_router
from .internal_auth import router as internal_auth_router
from .location import router as location_router
from .payment import router as payment_router
from .plan import router as plan_router
from .region import router as region_router
from .role import router as role_router
from .root import router as root_router
from .sim import router as sim_router
from .store import router as store_router
from .user import router as user_router
from .account_type import router as account_type_router
from .store_contact import router as store_contact_router

__all__ = [
    "action_router",
    "analytics_router",
    "auth_router",
    "city_router",
    "configuration_router",
    "country_router",
    "device_router",
    "enrolment_router",
    "internal_auth_router",
    "location_router",
    "payment_router",
    "plan_router",
    "region_router",
    "role_router",
    "root_router",
    "sim_router",
    "store_router",
    "user_router",
    "factory_reset_protection_router",
    "account_type_router",
    "store_contact_router",
]
