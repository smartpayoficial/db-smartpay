"""
Script para corregir problemas de zona horaria en la base de datos.

Este script configura la zona horaria de PostgreSQL para evitar problemas
con fechas 'aware' y 'naive' en Tortoise ORM.
"""

import asyncio
import os
from tortoise import Tortoise

# Configuración de la base de datos
DB_URL = os.getenv("POSTGRES_DATABASE_URL", "postgres://postgres:postgres@smartpay-db-v12:5432/smartpay")

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
    
    print("Zona horaria configurada correctamente.")
    
    await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(fix_timezone())
