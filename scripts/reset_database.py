#!/usr/bin/env python3
"""
Script para eliminar y recrear la base de datos PostgreSQL en la VPS
"""
import asyncio
import logging
import os
import re
from sys import argv

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from app.config import settings

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
    """Elimina y recrea la base de datos"""
    # Extraer información de conexión
    try:
        db_info = parse_db_url(settings.POSTGRES_DATABASE_URL)
    except ValueError as e:
        logger.error(f"Error al analizar la URL de la base de datos: {e}")
        return
    
    dbname = db_info['dbname']
    user = db_info['user']
    password = db_info['password']
    host = db_info['host']
    port = db_info['port']
    
    logger.info(f"Preparando para resetear la base de datos: {dbname} en {host}:{port}")
    
    # Confirmar antes de eliminar
    if len(argv) <= 1 or argv[1] != "--force":
        confirm = input(f"¿Estás seguro de que deseas ELIMINAR y RECREAR la base de datos '{dbname}'? (s/N): ")
        if confirm.lower() != 's':
            logger.info("Operación cancelada.")
            return
    
    # Conectar a postgres para poder eliminar/crear bases de datos
    try:
        conn = psycopg2.connect(
            dbname='postgres',
            user=user,
            password=password,
            host=host,
            port=port
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Cerrar conexiones activas a la base de datos
        logger.info(f"Cerrando conexiones activas a {dbname}...")
        cursor.execute(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{dbname}'
            AND pid <> pg_backend_pid();
        """)
        
        # Eliminar la base de datos
        logger.info(f"Eliminando base de datos: {dbname}")
        cursor.execute(f"DROP DATABASE IF EXISTS {dbname};")
        
        # Crear la base de datos nuevamente
        logger.info(f"Creando base de datos: {dbname}")
        cursor.execute(f"CREATE DATABASE {dbname} WITH OWNER = {user};")
        
        cursor.close()
        conn.close()
        
        logger.info(f"Base de datos {dbname} ha sido eliminada y recreada exitosamente.")
        
        # Opcional: Generar esquemas
        if len(argv) > 1 and argv[1] == "--with-schema":
            logger.info("Generando esquemas...")
            from app.infra.postgres.config import generate_schema
            await generate_schema()
            logger.info("Esquemas generados exitosamente.")
            
        # Opcional: Cargar datos por defecto
        if len(argv) > 1 and argv[1] == "--with-defaults":
            logger.info("Cargando datos por defecto...")
            from app.infra.postgres.config import generate_records_defaults
            await generate_records_defaults()
            logger.info("Datos por defecto cargados exitosamente.")
            
    except Exception as e:
        logger.error(f"Error al resetear la base de datos: {e}")

if __name__ == "__main__":
    # Verificar si psycopg2 está instalado
    try:
        import psycopg2
    except ImportError:
        logger.error("El paquete psycopg2 no está instalado. Instalándolo...")
        os.system("pip install psycopg2-binary")
        
    asyncio.run(reset_database())
