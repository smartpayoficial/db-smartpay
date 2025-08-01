#!/usr/bin/env python3
"""
Script para solucionar directamente el problema de fechas en la base de datos.
Este script no depende de la importación del módulo 'app' y puede ejecutarse directamente.
"""
import asyncio
import datetime
import logging
import os
import sys

# Agregar el directorio raíz al path para poder importar los módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configurar logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def fix_database_connection():
    try:
        # Importar Tortoise ORM
        from tortoise import Tortoise
        
        # Obtener la URL de la base de datos del entorno o usar un valor predeterminado
        db_url = os.environ.get("DATABASE_URL", "postgres://postgres:postgres@localhost:5432/smartpay")
        
        # Conectar a la base de datos
        await Tortoise.init(
            db_url=db_url,
            modules={"models": ["app.infra.postgres.models"]}
        )
        
        logger.info("Conexión a la base de datos establecida correctamente")
        return True
    except Exception as e:
        logger.error(f"Error al conectar a la base de datos: {e}")
        return False

async def execute_sql_fix():
    """
    Ejecuta SQL directo para solucionar el problema de zonas horarias en la base de datos.
    """
    try:
        from tortoise import connections
        
        # Obtener conexión
        connection = connections.get("default")
        
        # Ejecutar SQL para configurar el manejo de zonas horarias
        await connection.execute_script("""
        -- Configurar la zona horaria de la sesión a UTC
        SET timezone = 'UTC';
        
        -- Actualizar la configuración de PostgreSQL para manejar fechas sin zona horaria
        ALTER DATABASE CURRENT_SET timezone = 'UTC';
        """)
        
        logger.info("Configuración de zona horaria aplicada correctamente")
        return True
    except Exception as e:
        logger.error(f"Error al ejecutar SQL: {e}")
        return False

async def main():
    logger.info("Iniciando corrección de problema de fechas...")
    
    # Conectar a la base de datos
    if not await fix_database_connection():
        logger.error("No se pudo establecer conexión a la base de datos. Abortando.")
        return
    
    # Aplicar corrección SQL
    if await execute_sql_fix():
        logger.info("Corrección aplicada correctamente.")
    else:
        logger.error("No se pudo aplicar la corrección.")
    
    # Cerrar conexiones
    try:
        from tortoise import Tortoise
        await Tortoise.close_connections()
        logger.info("Conexiones cerradas correctamente")
    except Exception as e:
        logger.error(f"Error al cerrar conexiones: {e}")

if __name__ == "__main__":
    asyncio.run(main())
