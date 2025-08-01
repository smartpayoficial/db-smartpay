#!/usr/bin/env python3
"""
Script para detener el contenedor, corregir el error y reiniciarlo.
"""
import os
import logging
import subprocess
import time

# Configurar logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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

def create_patch_file():
    """Crea el archivo de parche en el directorio actual"""
    patch_file = "tortoise_patch.py"
    
    try:
        with open(patch_file, "w") as f:
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
        logger.info(f"Archivo de parche creado: {patch_file}")
        return True
    except Exception as e:
        logger.error(f"Error al crear el archivo de parche: {e}")
        return False

def start_container():
    """Inicia el contenedor Docker"""
    try:
        result = subprocess.run(
            "docker start smartpay-db-api",
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

def copy_patch_to_container():
    """Copia el archivo de parche al contenedor Docker"""
    try:
        # Esperar a que el contenedor esté en ejecución
        time.sleep(5)
        
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

def fix_init_file():
    """Corrige el archivo __init__.py de Tortoise ORM"""
    try:
        # Crear un archivo temporal con el contenido correcto
        with open("tortoise_init_patch.py", "w") as f:
            f.write("""
# Importar parche de zona horaria
try:
    import tortoise_patch
except ImportError:
    pass
""")
        
        # Copiar el archivo al contenedor
        result = subprocess.run(
            "docker cp tortoise_init_patch.py smartpay-db-api:/usr/local/lib/python3.8/site-packages/tortoise/",
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Ejecutar comando para corregir el archivo __init__.py
        cmd = """docker exec smartpay-db-api bash -c "grep -v 'try:\\\\n' /usr/local/lib/python3.8/site-packages/tortoise/__init__.py > /tmp/init_temp.py && mv /tmp/init_temp.py /usr/local/lib/python3.8/site-packages/tortoise/__init__.py && cat /usr/local/lib/python3.8/site-packages/tortoise/tortoise_init_patch.py >> /usr/local/lib/python3.8/site-packages/tortoise/__init__.py" """
        
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        logger.info("Archivo __init__.py corregido correctamente")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error al corregir el archivo __init__.py: {e}")
        logger.error(f"Salida de error: {e.stderr}")
        return False

def main():
    logger.info("Iniciando proceso de corrección del contenedor...")
    
    # Detener el contenedor
    if not stop_container():
        logger.error("No se pudo detener el contenedor. Abortando.")
        return
    
    # Crear el archivo de parche
    if not create_patch_file():
        logger.error("No se pudo crear el archivo de parche. Abortando.")
        return
    
    # Iniciar el contenedor
    if not start_container():
        logger.error("No se pudo iniciar el contenedor. Abortando.")
        return
    
    # Copiar el archivo de parche al contenedor
    if not copy_patch_to_container():
        logger.error("No se pudo copiar el archivo de parche al contenedor. Abortando.")
        return
    
    # Corregir el archivo __init__.py
    if not fix_init_file():
        logger.error("No se pudo corregir el archivo __init__.py. Abortando.")
        return
    
    # Reiniciar el contenedor
    if not stop_container() or not start_container():
        logger.error("No se pudo reiniciar el contenedor. Abortando.")
        return
    
    logger.info("Proceso completado correctamente.")
    logger.info("Espera unos segundos para que el contenedor se inicie completamente.")
    logger.info("Luego puedes probar la creación de usuarios nuevamente.")

if __name__ == "__main__":
    main()
