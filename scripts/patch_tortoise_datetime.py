#!/usr/bin/env python3
"""
Script para parchar Tortoise ORM y resolver el problema de zonas horarias.
Este script crea un archivo de configuración que será cargado por la aplicación.
"""
import os
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_patch_file():
    """Crea un archivo de parche para Tortoise ORM"""
    
    # Ruta del archivo de parche
    patch_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                  'app', 'infra', 'postgres', 'timezone_patch.py')
    
    # Contenido del parche
    patch_content = """
# Archivo de parche para corregir problemas de zona horaria en Tortoise ORM
# Este archivo debe ser importado al inicio de la aplicación

import datetime
import pytz
from tortoise import fields

# Guardar la implementación original
original_datetime_field_to_db_value = fields.DatetimeField.to_db_value

# Parchar el método to_db_value para asegurar que todas las fechas sean UTC sin zona horaria
async def patched_to_db_value(self, value, instance):
    if value is not None:
        # Si la fecha tiene información de zona horaria, convertirla a UTC y quitar la zona horaria
        if hasattr(value, 'tzinfo') and value.tzinfo is not None:
            value = value.astimezone(pytz.UTC).replace(tzinfo=None)
    
    # Llamar a la implementación original con la fecha corregida
    return await original_datetime_field_to_db_value(self, value, instance)

# Aplicar el parche
fields.DatetimeField.to_db_value = patched_to_db_value

# Registrar que el parche ha sido aplicado
print("Parche de zona horaria aplicado a Tortoise ORM")
"""
    
    try:
        # Crear el directorio si no existe
        os.makedirs(os.path.dirname(patch_file_path), exist_ok=True)
        
        # Escribir el archivo de parche
        with open(patch_file_path, 'w') as f:
            f.write(patch_content)
        
        logger.info(f"Archivo de parche creado en: {patch_file_path}")
        return True
    except Exception as e:
        logger.error(f"Error al crear el archivo de parche: {e}")
        return False

def create_init_patch():
    """Modifica el archivo __init__.py para importar el parche"""
    
    # Ruta del archivo __init__.py
    init_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                 'app', 'infra', 'postgres', '__init__.py')
    
    # Contenido a agregar
    import_line = "\n# Importar parche de zona horaria\ntry:\n    from .timezone_patch import *\nexcept ImportError:\n    pass\n"
    
    try:
        # Leer el contenido actual
        try:
            with open(init_file_path, 'r') as f:
                current_content = f.read()
        except FileNotFoundError:
            current_content = ""
        
        # Verificar si el parche ya está importado
        if "from .timezone_patch import" not in current_content:
            # Agregar la importación
            with open(init_file_path, 'w') as f:
                f.write(current_content + import_line)
            
            logger.info(f"Archivo __init__.py modificado: {init_file_path}")
        else:
            logger.info("El parche ya está importado en __init__.py")
        
        return True
    except Exception as e:
        logger.error(f"Error al modificar el archivo __init__.py: {e}")
        return False

def main():
    logger.info("Iniciando la aplicación del parche de zona horaria...")
    
    # Crear el archivo de parche
    if create_patch_file():
        logger.info("Archivo de parche creado correctamente.")
    else:
        logger.error("No se pudo crear el archivo de parche.")
        return
    
    # Modificar el archivo __init__.py
    if create_init_patch():
        logger.info("Archivo __init__.py modificado correctamente.")
    else:
        logger.error("No se pudo modificar el archivo __init__.py.")
        return
    
    logger.info("Parche aplicado correctamente. Reinicie la aplicación para que los cambios surtan efecto.")

if __name__ == "__main__":
    main()
