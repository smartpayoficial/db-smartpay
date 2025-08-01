#!/usr/bin/env python3
"""
Script para eliminar todas las tablas de la base de datos PostgreSQL
"""
import asyncio
import logging
from sys import argv

from tortoise import Tortoise

from app.config import settings
from app.infra.postgres.config import TORTOISE_ORM

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def drop_all_tables():
    """Elimina todas las tablas de la base de datos"""
    logger.info("Conectando a la base de datos...")
    await Tortoise.init(config=TORTOISE_ORM)
    
    connection = Tortoise.get_connection("default")
    
    logger.info("Obteniendo todas las tablas...")
    # Obtener todas las tablas excluyendo las del esquema pg_
    result = await connection.execute_query("""
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'public'
    """)
    
    tables = [row[0] for row in result[1]]
    
    if not tables:
        logger.info("No se encontraron tablas para eliminar.")
        return
    
    logger.info(f"Se encontraron {len(tables)} tablas: {', '.join(tables)}")
    
    # Confirmar antes de eliminar
    if len(argv) <= 1 or argv[1] != "--force":
        confirm = input(f"¿Estás seguro de que deseas eliminar TODAS las tablas? (s/N): ")
        if confirm.lower() != 's':
            logger.info("Operación cancelada.")
            return
    
    # Desactivar restricciones de clave foránea temporalmente
    await connection.execute_query("SET CONSTRAINTS ALL DEFERRED;")
    
    # Eliminar todas las tablas
    for table in tables:
        logger.info(f"Eliminando tabla: {table}")
        try:
            await connection.execute_query(f'DROP TABLE IF EXISTS "{table}" CASCADE;')
        except Exception as e:
            logger.error(f"Error al eliminar la tabla {table}: {e}")
    
    logger.info("Todas las tablas han sido eliminadas.")
    await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(drop_all_tables())
