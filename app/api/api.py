from fastapi import APIRouter

from app.api.routers import root, user

api_router = APIRouter()
api_router.include_router(root.router, prefix="/health-check", tags=["Health Check"])
api_router.include_router(user.router, prefix="/user", tags=["User"])
