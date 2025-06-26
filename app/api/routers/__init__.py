from app.api.routers.city import router as city_router
from app.api.routers.configuration import router as configuration_router
from app.api.routers.country import router as country_router
from app.api.routers.device import router as device_router
from app.api.routers.enrolment import router as enrolment_router
from app.api.routers.internal_auth import router as internal_auth_router
from app.api.routers.region import router as region_router
from app.api.routers.role import router as role_router
from app.api.routers.payment import router as payment_router
from app.api.routers.plan import router as plan_router
from app.api.routers.sim import router as sim_router
from app.api.routers.user import router as user_router
from app.api.routers.action import router as action_router

# Re-export the routers
city = city_router
configuration = configuration_router
country = country_router
device = device_router
enrolment = enrolment_router
internal_auth = internal_auth_router
region = region_router
role = role_router
payment = payment_router
plan = plan_router
sim = sim_router
user = user_router
action = action_router

__all__ = [
    "city",
    "configuration",
    "country",
    "device",
    "enrolment",
    "internal_auth",
    "region",
    "role",
    "payment",
    "plan",
    "sim",
    "user",
    "action",
]
