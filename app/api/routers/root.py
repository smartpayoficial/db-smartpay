from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.config import settings
from app.schemas.root import HealtCheck

router = APIRouter()


@router.get(
    "",
    response_class=JSONResponse,
    response_model=HealtCheck,
    status_code=200,
    responses={
        200: {"description": "Healt check found"},
    },
)
async def healt_check():
    return {
        "title": settings.TITLE,
        "version": settings.VERSION,
        "description": settings.DESCRIPTION,
        "environment": settings.ENVIRONMENT,
    }
