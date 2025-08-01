#!/usr/bin/env python3
"""
Script para corregir directamente el problema de fechas en la base de datos.
Este script modifica la base de datos para usar fechas sin zona horaria.
"""
import os
import sys
import logging
import psycopg2
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_db_connection():
    """Obtiene una conexión a la base de datos"""
    try:
        # Intentar conectar a la base de datos
        conn = psycopg2.connect(
            host="localhost",
            port="5438",
            database="smartpay",
            user="postgres",
            password="postgres"
        )
        logger.info("Conexión a la base de datos establecida correctamente.")
        return conn
    except Exception as e:
        logger.error(f"Error al conectar a la base de datos: {e}")
        return None

def fix_datetime_issue(conn):
    """Aplica correcciones de zona horaria a la base de datos"""
    if conn is None:
        logger.error("No hay conexión a la base de datos.")
        return False
    
    try:
        # Crear un cursor
        cursor = conn.cursor()
        
        # Configurar la zona horaria a UTC
        cursor.execute("SET timezone TO 'UTC';")
        
        # Configurar la base de datos para usar UTC
        cursor.execute("ALTER DATABASE smartpay SET timezone TO 'UTC';")
        
        # Verificar la configuración
        cursor.execute("SHOW timezone;")
        timezone = cursor.fetchone()[0]
        logger.info(f"Zona horaria configurada a: {timezone}")
        
        # Crear una función para convertir fechas con zona horaria a fechas sin zona horaria
        cursor.execute("""
        CREATE OR REPLACE FUNCTION convert_to_naive_datetime(ts timestamptz) 
        RETURNS timestamp AS $$
        BEGIN
            RETURN ts AT TIME ZONE 'UTC';
        END;
        $$ LANGUAGE plpgsql;
        """)
        
        # Modificar la tabla user para usar fechas sin zona horaria
        try:
            cursor.execute("""
            ALTER TABLE "user" 
            ALTER COLUMN created_at TYPE timestamp USING convert_to_naive_datetime(created_at),
            ALTER COLUMN updated_at TYPE timestamp USING convert_to_naive_datetime(updated_at);
            """)
            logger.info("Tabla 'user' modificada correctamente.")
        except Exception as e:
            logger.error(f"Error al modificar la tabla 'user': {e}")
        
        # Confirmar los cambios
        conn.commit()
        logger.info("Cambios confirmados en la base de datos.")
        
        return True
    except Exception as e:
        logger.error(f"Error al aplicar correcciones: {e}")
        conn.rollback()
        return False
    finally:
        if conn:
            conn.close()
            logger.info("Conexión a la base de datos cerrada.")

def main():
    logger.info("Iniciando corrección de zonas horarias...")
    
    # Obtener conexión a la base de datos
    conn = get_db_connection()
    
    # Aplicar correcciones
    if fix_datetime_issue(conn):
        logger.info("Corrección de zonas horarias aplicada correctamente.")
    else:
        logger.error("No se pudo aplicar la corrección de zonas horarias.")
    
    logger.info("Proceso completado.")

if __name__ == "__main__":
    main()
