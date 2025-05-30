from fastapi import APIRouter

from app.api.routers import authentication_router, configuration_router, device_router

api_router = APIRouter()


# Health Check
@api_router.get("/health-check", tags=["Health Check"])
async def health_check():
    return {"status": "ok"}


# Configuration Management
api_router.include_router(
    configuration_router, prefix="/configurations", tags=["configurations"]
)
api_router.include_router(
    authentication_router, prefix="/authentications", tags=["authentications"]
)
api_router.include_router(device_router, prefix="/devices", tags=["devices"])
