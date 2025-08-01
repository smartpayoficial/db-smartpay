#!/usr/bin/env python3
"""
Script para crear un parche de Tortoise ORM dentro del contenedor Docker.
Este script crea un archivo Python que modifica directamente el código fuente de Tortoise ORM
para resolver el problema de zonas horarias.
"""
import os
import logging
import subprocess

# Configurar logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Contenido del parche para Tortoise ORM
PATCH_CONTENT = """
import datetime
from tortoise import fields

# Guardar la implementación original
original_to_db_value = fields.DatetimeField.to_db_value

# Función para convertir fechas con zona horaria a fechas sin zona horaria
def convert_to_naive_datetime(value):
    if value is not None and hasattr(value, 'tzinfo') and value.tzinfo is not None:
        # Convertir a UTC y quitar la información de zona horaria
        value = value.replace(tzinfo=None)
    return value

# Reemplazar el método to_db_value
def patched_to_db_value(self, value, instance):
    # Convertir a fecha sin zona horaria
    value = convert_to_naive_datetime(value)
    # Llamar a la implementación original
    return original_to_db_value(self, value, instance)

# Aplicar el parche
fields.DatetimeField.to_db_value = patched_to_db_value

print("Parche de Tortoise ORM aplicado correctamente")
"""

def create_patch_file():
    """Crea el archivo de parche en el directorio actual"""
    patch_file = "tortoise_patch.py"
    
    try:
        with open(patch_file, "w") as f:
            f.write(PATCH_CONTENT)
        logger.info(f"Archivo de parche creado: {patch_file}")
        return True
    except Exception as e:
        logger.error(f"Error al crear el archivo de parche: {e}")
        return False

def copy_to_container():
    """Copia el archivo de parche al contenedor Docker"""
    try:
        # Copiar el archivo al contenedor
        result = subprocess.run(
            "docker cp tortoise_patch.py smartpay-db-api:/usr/local/lib/python3.8/site-packages/",
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logger.info("Archivo de parche copiado al contenedor")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error al copiar el archivo al contenedor: {e}")
        logger.error(f"Salida de error: {e.stderr}")
        return False

def modify_init_file():
    """Modifica el archivo __init__.py de Tortoise para importar el parche"""
    try:
        # Comando para modificar el archivo __init__.py
        cmd = """docker exec smartpay-db-api bash -c "echo 'try:\\n    import tortoise_patch\\nexcept ImportError:\\n    pass' >> /usr/local/lib/python3.8/site-packages/tortoise/__init__.py" """
        
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logger.info("Archivo __init__.py modificado correctamente")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error al modificar el archivo __init__.py: {e}")
        logger.error(f"Salida de error: {e.stderr}")
        return False

def restart_container():
    """Reinicia el contenedor Docker"""
    try:
        result = subprocess.run(
            "docker restart smartpay-db-api",
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logger.info("Contenedor reiniciado correctamente")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error al reiniciar el contenedor: {e}")
        logger.error(f"Salida de error: {e.stderr}")
        return False

def main():
    logger.info("Iniciando el proceso de parchado de Tortoise ORM...")
    
    # Crear el archivo de parche
    if not create_patch_file():
        logger.error("No se pudo crear el archivo de parche. Abortando.")
        return
    
    # Copiar el archivo al contenedor
    if not copy_to_container():
        logger.error("No se pudo copiar el archivo al contenedor. Abortando.")
        return
    
    # Modificar el archivo __init__.py
    if not modify_init_file():
        logger.error("No se pudo modificar el archivo __init__.py. Abortando.")
        return
    
    # Reiniciar el contenedor
    if not restart_container():
        logger.error("No se pudo reiniciar el contenedor. Abortando.")
        return
    
    logger.info("Proceso de parchado completado correctamente.")
    logger.info("Ahora puedes probar la creación de usuarios nuevamente.")

if __name__ == "__main__":
    main()
