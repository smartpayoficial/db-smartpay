import asyncio

from passlib.context import CryptContext
from tortoise import Tortoise

from app.core.config import settings
from app.infra.postgres.models.user import User

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def migrate():
    # Inicializar Tortoise igual que en init_db()
    await Tortoise.init(
        db_url=settings.POSTGRES_DATABASE_URL,
        modules={"models": ["app.infra.postgres.models"]},
    )

    for u in await User.all():
        if not u.password.startswith("$2b$"):
            u.password = pwd.hash(u.password)
            await u.save()
            print("Hashed:", u.username)

    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(migrate())
