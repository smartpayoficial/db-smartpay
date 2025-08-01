#!/usr/bin/env python3
"""
Script para reconstruir el contenedor Docker con una configuración correcta de zonas horarias.
"""
import os
import logging
import subprocess
import time

# Configurar logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_timezone_patch():
    """Crea un archivo de parche para manejar zonas horarias"""
    try:
        # Crear directorio para el parche
        os.makedirs("timezone_patch", exist_ok=True)
        
        # Crear archivo __init__.py
        with open("timezone_patch/__init__.py", "w") as f:
            f.write("""
# Parche para manejar zonas horarias en Tortoise ORM
from .patch import *
""")
        
        # Crear archivo patch.py
        with open("timezone_patch/patch.py", "w") as f:
            f.write("""
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
""")
        
        # Crear archivo setup.py
        with open("timezone_patch/setup.py", "w") as f:
            f.write("""
from setuptools import setup, find_packages

setup(
    name="timezone_patch",
    version="0.1",
    packages=find_packages(),
)
""")
        
        logger.info("Archivos de parche creados correctamente")
        return True
    except Exception as e:
        logger.error(f"Error al crear archivos de parche: {e}")
        return False

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

def rebuild_container():
    """Reconstruye el contenedor Docker"""
    try:
        # Copiar archivos de parche al directorio del backend
        result = subprocess.run(
            "cp -r timezone_patch ~/backend-gateway-api/",
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Modificar el Dockerfile para instalar el parche
        dockerfile_path = os.path.expanduser("~/backend-gateway-api/Dockerfile")
        
        # Leer el contenido actual
        with open(dockerfile_path, "r") as f:
            content = f.read()
        
        # Buscar la línea donde se instalan las dependencias
        if "RUN pip install -r requirements.txt" in content:
            # Agregar la instalación del parche después de las dependencias
            content = content.replace(
                "RUN pip install -r requirements.txt",
                "RUN pip install -r requirements.txt\nCOPY timezone_patch /timezone_patch\nRUN pip install -e /timezone_patch"
            )
            
            # Escribir el contenido modificado
            with open(dockerfile_path, "w") as f:
                f.write(content)
            
            logger.info("Dockerfile modificado correctamente")
        else:
            logger.warning("No se encontró la línea para instalar dependencias en el Dockerfile")
        
        # Reconstruir la imagen
        result = subprocess.run(
            "cd ~/backend-gateway-api && docker build -t smartpay-db-api .",
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logger.info("Imagen reconstruida correctamente")
        
        # Iniciar el contenedor
        result = subprocess.run(
            "cd ~/backend-gateway-api && docker run -d --name smartpay-db-api -p 8002:8000 smartpay-db-api",
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logger.info("Contenedor iniciado correctamente")
        
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error al reconstruir el contenedor: {e}")
        logger.error(f"Salida de error: {e.stderr}")
        return False

def main():
    logger.info("Iniciando proceso de reconstrucción del contenedor...")
    
    # Crear archivos de parche
    if not create_timezone_patch():
        logger.error("No se pudieron crear los archivos de parche. Abortando.")
        return
    
    # Detener el contenedor
    if not stop_container():
        logger.warning("No se pudo detener el contenedor. Intentando eliminarlo de todas formas.")
    
    # Eliminar el contenedor
    if not remove_container():
        logger.warning("No se pudo eliminar el contenedor. Intentando reconstruirlo de todas formas.")
    
    # Reconstruir el contenedor
    if not rebuild_container():
        logger.error("No se pudo reconstruir el contenedor. Abortando.")
        return
    
    logger.info("Proceso completado correctamente.")
    logger.info("Espera unos segundos para que el contenedor se inicie completamente.")
    logger.info("Luego puedes probar la creación de usuarios nuevamente.")

if __name__ == "__main__":
    main()
