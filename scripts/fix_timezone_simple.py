#!/usr/bin/env python3
"""
Script simple para corregir el problema de zonas horarias en la base de datos.
Este script utiliza psycopg2 directamente sin depender de los módulos de la aplicación.
"""
import os
import sys
import logging
import subprocess

# Configurar logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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
        
        logger.info(f"Comando ejecutado correctamente: {command}")
        logger.info(f"Resultado: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error al ejecutar comando: {e}")
        logger.error(f"Salida de error: {e.stderr}")
        return False

def fix_timezone():
    """Aplica correcciones de zona horaria a la base de datos"""
    logger.info("Aplicando correcciones de zona horaria...")
    
    # Comandos SQL para corregir la zona horaria
    commands = [
        "SET timezone = 'UTC';",
        "ALTER DATABASE CURRENT_SET timezone = 'UTC';",
        "SHOW timezone;"
    ]
    
    # Ejecutar cada comando
    success = True
    for cmd in commands:
        if not run_sql_command(cmd):
            success = False
    
    return success

def main():
    logger.info("Iniciando corrección de zonas horarias...")
    
    if fix_timezone():
        logger.info("Corrección de zonas horarias aplicada correctamente.")
        logger.info("La base de datos ahora está configurada para usar UTC de manera consistente.")
    else:
        logger.error("No se pudo aplicar la corrección de zonas horarias.")
    
    logger.info("Proceso completado.")

if __name__ == "__main__":
    main()
