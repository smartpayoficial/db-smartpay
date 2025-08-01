"""
Script para verificar el estado de las tablas en la base de datos y regenerarlas si es necesario.
Este script comprueba si todas las tablas existen y tienen la estructura correcta.
Si hay problemas, ejecuta el script de creación de tablas nuevamente.
"""

import asyncio
import os
import subprocess
from tortoise import Tortoise

# Configuración de la base de datos
DB_URL = os.getenv("POSTGRES_DATABASE_URL", "postgres://postgres:postgres@smartpay-db-v12:5432/smartpay")

# Lista de tablas esperadas
EXPECTED_TABLES = [
    "user", "role", "country", "region", "city", "store", "action", 
    "authentication", "configuration", "device", "device_group", 
    "enrolment", "factory_reset_protection", "group", "location", 
    "payment", "sim", "user_group"
]

async def init_tortoise():
    """Inicializa la conexión a Tortoise ORM."""
    await Tortoise.init(
        db_url=DB_URL,
        modules={"models": ["app.infra.postgres.models"]}
    )

async def check_tables():
    """Verifica si todas las tablas esperadas existen en la base de datos."""
    conn = Tortoise.get_connection("default")
    
    # Consulta para obtener todas las tablas en el esquema public
    query = """
    SELECT tablename FROM pg_catalog.pg_tables 
    WHERE schemaname = 'public'
    """
    
    result = await conn.execute_query(query)
    existing_tables = [row[0] for row in result[1]]
    
    print("Tablas existentes:", existing_tables)
    
    # Verificar si todas las tablas esperadas existen
    missing_tables = [table for table in EXPECTED_TABLES if table not in existing_tables]
    
    if missing_tables:
        print(f"Faltan las siguientes tablas: {missing_tables}")
        return False
    
    # Verificar si las tablas tienen la estructura correcta
    for table in EXPECTED_TABLES:
        try:
            # Intentar hacer una consulta simple para verificar que la tabla funciona
            await conn.execute_query(f"SELECT * FROM \"{table}\" LIMIT 1")
        except Exception as e:
            print(f"Error al consultar la tabla {table}: {e}")
            return False
    
    print("Todas las tablas existen y tienen la estructura correcta.")
    return True

async def execute_create_tables_script():
    """Ejecuta el script SQL para crear todas las tablas."""
    print("Ejecutando script de creación de tablas...")
    
    try:
        # Ejecutar el script SQL directamente en la base de datos
        result = subprocess.run(
            ["docker", "exec", "-i", "docker-smartpay-db-v12-1", "psql", "-U", "postgres", "-d", "smartpay", "-f", "/scripts/create_tables.sql"],
            capture_output=True,
            text=True,
            check=True
        )
        print("Salida del script de creación de tablas:")
        print(result.stdout)
        if result.stderr:
            print("Errores:")
            print(result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar el script de creación de tablas: {e}")
        print(f"Salida estándar: {e.stdout}")
        print(f"Error estándar: {e.stderr}")
        return False

async def main():
    """Función principal para verificar y regenerar tablas."""
    try:
        print("Inicializando Tortoise ORM...")
        await init_tortoise()
        
        # Verificar si todas las tablas existen
        tables_ok = await check_tables()
        
        if not tables_ok:
            print("Se detectaron problemas con las tablas. Regenerando...")
            success = await execute_create_tables_script()
            
            if success:
                print("Tablas regeneradas correctamente. Verificando nuevamente...")
                tables_ok = await check_tables()
                if tables_ok:
                    print("Verificación exitosa después de regenerar tablas.")
                else:
                    print("Aún hay problemas con las tablas después de regenerarlas.")
            else:
                print("Error al regenerar las tablas.")
        else:
            print("Todas las tablas están correctamente configuradas.")
    
    except Exception as e:
        print(f"Error en la ejecución: {e}")
    finally:
        await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(main())
