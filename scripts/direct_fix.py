#!/usr/bin/env python3
"""
Script para aplicar una solución directa al problema de zonas horarias.
Este script:
1. Modifica la base de datos para usar UTC
2. Convierte las columnas de fecha a timestamp sin zona horaria
3. Reinicia el contenedor de la API
"""
import os
import logging
import subprocess
import time

# Configurar logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_sql_command(command):
    """Ejecuta un comando SQL en el contenedor de Docker de la base de datos"""
    try:
        # Comando para ejecutar SQL en el contenedor de Docker
        docker_command = f'docker exec -i docker-smartpay-db-v12-1 psql -U postgres -d smartpay -c "{command}"'
        
        # Ejecutar el comando
        result = subprocess.run(
            docker_command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        logger.info(f"Comando SQL ejecutado correctamente: {command}")
        logger.info(f"Resultado: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error al ejecutar comando SQL: {e}")
        logger.error(f"Salida de error: {e.stderr}")
        return False

def fix_database_timezone():
    """Configura la base de datos para usar UTC"""
    logger.info("Configurando la base de datos para usar UTC...")
    
    # Comandos SQL para configurar la zona horaria
    commands = [
        "SET timezone TO 'UTC';",
        "ALTER DATABASE smartpay SET timezone TO 'UTC';",
        "SHOW timezone;"
    ]
    
    # Ejecutar cada comando
    success = True
    for cmd in commands:
        if not run_sql_command(cmd):
            success = False
    
    if success:
        logger.info("Base de datos configurada para usar UTC correctamente.")
    else:
        logger.error("No se pudo configurar la base de datos completamente.")
    
    return success

def convert_datetime_columns():
    """Convierte las columnas de fecha a timestamp sin zona horaria"""
    logger.info("Convirtiendo columnas de fecha a timestamp sin zona horaria...")
    
    # Comandos SQL para convertir columnas de fecha
    commands = [
        # Convertir columnas de la tabla user
        "ALTER TABLE \"user\" ALTER COLUMN created_at TYPE timestamp without time zone;",
        "ALTER TABLE \"user\" ALTER COLUMN updated_at TYPE timestamp without time zone;",
        
        # Convertir columnas de otras tablas que puedan tener el mismo problema
        "ALTER TABLE \"plan\" ALTER COLUMN created_at TYPE timestamp without time zone;",
        "ALTER TABLE \"plan\" ALTER COLUMN updated_at TYPE timestamp without time zone;",
        
        "ALTER TABLE \"payment\" ALTER COLUMN created_at TYPE timestamp without time zone;",
        "ALTER TABLE \"payment\" ALTER COLUMN updated_at TYPE timestamp without time zone;",
        
        "ALTER TABLE \"device\" ALTER COLUMN created_at TYPE timestamp without time zone;",
        "ALTER TABLE \"device\" ALTER COLUMN updated_at TYPE timestamp without time zone;",
        
        "ALTER TABLE \"store\" ALTER COLUMN created_at TYPE timestamp without time zone;",
        "ALTER TABLE \"store\" ALTER COLUMN updated_at TYPE timestamp without time zone;"
    ]
    
    # Ejecutar cada comando, ignorando errores si la tabla o columna no existe
    for cmd in commands:
        try:
            run_sql_command(cmd)
        except Exception as e:
            logger.warning(f"Error al ejecutar {cmd}: {e}")
    
    logger.info("Conversión de columnas completada.")
    return True

def stop_container():
    """Detiene el contenedor Docker"""
    try:
        result = subprocess.run(
            "docker stop smartpay-db-api",
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logger.info("Contenedor detenido correctamente")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error al detener el contenedor: {e}")
        logger.error(f"Salida de error: {e.stderr}")
        return False

def remove_container():
    """Elimina el contenedor Docker"""
    try:
        result = subprocess.run(
            "docker rm smartpay-db-api",
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logger.info("Contenedor eliminado correctamente")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error al eliminar el contenedor: {e}")
        logger.error(f"Salida de error: {e.stderr}")
        return False

def run_container():
    """Ejecuta el contenedor Docker con variables de entorno para zonas horarias"""
    try:
        # Ejecutar el contenedor con variables de entorno para zonas horarias
        cmd = """
        docker run -d --name smartpay-db-api \
        -p 8002:8000 \
        -e TZ=UTC \
        -e PYTHONPATH=/usr/src/app \
        smartpay-db-api
        """
        
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logger.info("Contenedor iniciado correctamente")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error al iniciar el contenedor: {e}")
        logger.error(f"Salida de error: {e.stderr}")
        return False

def main():
    logger.info("Iniciando solución directa para el problema de zonas horarias...")
    
    # Paso 1: Configurar la base de datos
    if not fix_database_timezone():
        logger.error("No se pudo configurar la base de datos. Abortando.")
        return
    
    # Paso 2: Convertir columnas de fecha
    if not convert_datetime_columns():
        logger.error("No se pudieron convertir las columnas de fecha. Abortando.")
        return
    
    # Paso 3: Detener el contenedor
    if not stop_container():
        logger.warning("No se pudo detener el contenedor. Intentando eliminarlo de todas formas.")
    
    # Paso 4: Eliminar el contenedor
    if not remove_container():
        logger.warning("No se pudo eliminar el contenedor. Intentando ejecutarlo de todas formas.")
    
    # Paso 5: Ejecutar el contenedor
    if not run_container():
        logger.error("No se pudo ejecutar el contenedor. Abortando.")
        return
    
    logger.info("Solución directa aplicada correctamente.")
    logger.info("Espera unos segundos para que el contenedor se inicie completamente.")
    logger.info("Luego puedes probar la creación de usuarios nuevamente.")

if __name__ == "__main__":
    main()
