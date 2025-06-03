from fastapi import APIRouter

from app.api.routers import (
    authentication_router,
    city_router,
    configuration_router,
    country_router,
    device_router,
    enrolment_router,
    region_router,
    role_router,
    user_router,
)

api_router = APIRouter()


# Health Check
@api_router.get("/health-check", tags=["Health Check"])
async def health_check():
    return {"status": "ok"}


# All CRUD endpoints
api_router.include_router(
    authentication_router, prefix="/authentications", tags=["authentications"]
)
api_router.include_router(city_router, prefix="/cities", tags=["cities"])
api_router.include_router(
    configuration_router, prefix="/configurations", tags=["configurations"]
)
api_router.include_router(country_router, prefix="/countries", tags=["countries"])
api_router.include_router(device_router, prefix="/devices", tags=["devices"])
api_router.include_router(enrolment_router, prefix="/enrolments", tags=["enrolments"])
api_router.include_router(region_router, prefix="/regions", tags=["regions"])
api_router.include_router(role_router, prefix="/roles", tags=["roles"])
api_router.include_router(user_router, prefix="/users", tags=["users"])
