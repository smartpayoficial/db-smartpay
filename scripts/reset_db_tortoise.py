#!/usr/bin/env python3
"""
Script para eliminar y recrear la base de datos PostgreSQL usando Tortoise ORM
"""
import asyncio
import logging
import re
from sys import argv

from tortoise import Tortoise

from app.config import settings
from app.infra.postgres.config import TORTOISE_ORM

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_db_url(url):
    """Extrae los componentes de la URL de la base de datos"""
    pattern = r'postgres(?:ql)?://(?P<user>[^:]+):(?P<password>[^@]+)@(?P<host>[^:]+):(?P<port>\d+)/(?P<dbname>[^?]+)'
    match = re.match(pattern, url)
    if not match:
        raise ValueError("Formato de URL de base de datos inválido")
    return match.groupdict()

async def reset_database():
    """Elimina todas las tablas y recrea los esquemas"""
    logger.info("Conectando a la base de datos...")
    
    # Confirmar antes de eliminar
    if len(argv) <= 1 or argv[1] != "--force":
        confirm = input(f"¿Estás seguro de que deseas ELIMINAR TODAS LAS TABLAS de la base de datos? (s/N): ")
        if confirm.lower() != 's':
            logger.info("Operación cancelada.")
            return
    
    try:
        # Inicializar Tortoise ORM
        await Tortoise.init(config=TORTOISE_ORM)
        connection = Tortoise.get_connection("default")
        
        # Obtener todas las tablas
        logger.info("Obteniendo todas las tablas...")
        result = await connection.execute_query("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public'
        """)
        
        tables = [row[0] for row in result[1]]
        
        if not tables:
            logger.info("No se encontraron tablas para eliminar.")
        else:
            logger.info(f"Se encontraron {len(tables)} tablas: {', '.join(tables)}")
            
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
        
        # Regenerar esquemas
        if len(argv) > 1 and (argv[1] == "--with-schema" or argv[1] == "--force"):
            logger.info("Regenerando esquemas...")
            await Tortoise.generate_schemas()
            logger.info("Esquemas regenerados exitosamente.")
        
        # Cargar datos por defecto
        if len(argv) > 1 and argv[1] == "--with-defaults":
            logger.info("Cargando datos por defecto...")
            from app.infra.postgres.config import generate_records_defaults
            await generate_records_defaults()
            logger.info("Datos por defecto cargados exitosamente.")
        
    except Exception as e:
        logger.error(f"Error durante la operación: {e}")
    finally:
        # Cerrar conexiones
        await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(reset_database())
