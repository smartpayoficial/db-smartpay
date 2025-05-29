from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.api import api_router
from app.config import settings
from app.debugger import initialize_fastapi_server_debugger_if_needed
from app.infra.postgres.config import (
    generate_records_defaults,
    generate_schema,
    init_db,
)


def create_application():
    initialize_fastapi_server_debugger_if_needed()

    app = FastAPI(
        title=settings.TITLE,
        description=settings.DESCRIPTION,
        version=settings.VERSION,
    )
    app.include_router(api_router)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app


app = create_application()


@app.on_event("startup")
async def startup_event():
    init_db(app)
    await generate_schema()
    if settings.DEFAULT_DATA:
        await generate_records_defaults()
