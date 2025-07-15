from fastapi import APIRouter

from app.api.routers import (
    action_router,
    auth_router,
    city_router,
    configuration_router,
    country_router,
    device_router,
    enrolment_router,
    factory_reset_protection_router,
    internal_auth_router,
    location_router,
    payment_router,
    plan_router,
    region_router,
    role_router,
    root_router,
    sim_router,
    store_router,
    user_router,
)

api_router = APIRouter()

# Root router (e.g., for health checks)
api_router.include_router(root_router, tags=["Root"])

# Include all other routers
api_router.include_router(action_router, prefix="/actions", tags=["actions"])
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(city_router, prefix="/cities", tags=["cities"])
api_router.include_router(
    configuration_router, prefix="/configurations", tags=["configurations"]
)
api_router.include_router(country_router, prefix="/countries", tags=["countries"])
api_router.include_router(device_router, prefix="/devices", tags=["devices"])
api_router.include_router(enrolment_router, prefix="/enrolments", tags=["enrolments"])
api_router.include_router(
    factory_reset_protection_router,
    prefix="/factory-reset-protections",
    tags=["factory-reset-protections"],
)
api_router.include_router(internal_auth_router, tags=["internal_auth"])
api_router.include_router(location_router, prefix="/locations", tags=["locations"])
api_router.include_router(payment_router, prefix="/payments", tags=["payments"])
api_router.include_router(plan_router, prefix="/plans", tags=["plans"])
api_router.include_router(region_router, prefix="/regions", tags=["regions"])
api_router.include_router(role_router, prefix="/roles", tags=["roles"])
api_router.include_router(sim_router, prefix="/sims", tags=["sims"])
api_router.include_router(store_router, prefix="/stores", tags=["stores"])
api_router.include_router(user_router, prefix="/users", tags=["users"])
