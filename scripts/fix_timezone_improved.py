"""
Script para corregir problemas de zona horaria en la base de datos.

Este script configura la zona horaria de PostgreSQL para evitar problemas
con fechas 'aware' y 'naive' en Tortoise ORM, y también configura el entorno
de Python para usar UTC.
"""

import asyncio
import os
import datetime
from tortoise import Tortoise

# Configuración de la base de datos
DB_URL = os.getenv("POSTGRES_DATABASE_URL", "postgres://postgres:postgres@smartpay-db-v12:5432/smartpay")

# Configurar zona horaria en Python
os.environ['TZ'] = 'UTC'
try:
    # En algunos sistemas esto es necesario para aplicar el cambio de TZ
    import time
    time.tzset()
except AttributeError:
    # Windows no tiene tzset
    pass

async def fix_timezone():
    """Configura la zona horaria de PostgreSQL para evitar problemas con fechas."""
    print("Conectando a la base de datos...")
    await Tortoise.init(
        db_url=DB_URL,
        modules={"models": ["app.infra.postgres.models"]}
    )
    
    # Obtener conexión
    conn = Tortoise.get_connection("default")
    
    print("Configurando zona horaria...")
    # Configurar la zona horaria de la sesión actual
    await conn.execute_query("SET TIME ZONE 'UTC';")
    
    # Configurar la zona horaria de forma permanente para la base de datos
    await conn.execute_query("ALTER DATABASE smartpay SET timezone TO 'UTC';")
    
    # Configurar parámetros de fecha en PostgreSQL
    await conn.execute_query("ALTER DATABASE smartpay SET datestyle TO 'ISO, YMD';")
    
    # Verificar la configuración
    result = await conn.execute_query("SHOW timezone;")
    print(f"Zona horaria de PostgreSQL: {result[1][0][0]}")
    
    result = await conn.execute_query("SHOW datestyle;")
    print(f"Estilo de fecha de PostgreSQL: {result[1][0][0]}")
    
    print("Zona horaria configurada correctamente.")
    print(f"Hora actual en Python: {datetime.datetime.now()}")
    
    await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(fix_timezone())
