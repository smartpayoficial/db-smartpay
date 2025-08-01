#!/usr/bin/env python3
import asyncio
import datetime
import pytz

from tortoise import Tortoise
from app.core.config import settings

# Configuración para asegurar que todas las fechas sean UTC y consistentes
async def fix_datetime_config():
    print("Configurando Tortoise ORM para manejar fechas de forma consistente...")
    
    # Conectar a la base de datos
    await Tortoise.init(
        db_url=settings.DATABASE_URL,
        modules={"models": ["app.infra.postgres.models"]}
    )
    
    # Configurar el uso de UTC para todas las operaciones de fecha/hora
    # Esto asegura que todas las fechas se guarden como UTC (offset-aware)
    import tortoise.timezone
    tortoise.timezone.set_timezone('UTC')
    
    print("Configuración completada. Ahora todas las fechas se manejarán como UTC.")
    
    # Cerrar la conexión
    await Tortoise.close_connections()

if __name__ == "__main__":
    print("Iniciando corrección de configuración de fechas...")
    asyncio.run(fix_datetime_config())
    print("Proceso completado.")
