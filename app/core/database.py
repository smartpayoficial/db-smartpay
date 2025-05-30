from tortoise import Tortoise

from app.core.config import settings


async def init_db():
    await Tortoise.init(
        db_url=settings.POSTGRES_DATABASE_URL,
        modules={"models": ["app.infra.postgres.models"]},
    )
    await Tortoise.generate_schemas()
