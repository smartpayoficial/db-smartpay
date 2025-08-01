#!/usr/bin/env python3
"""
Script integral para resolver el problema de zonas horarias en la creación de usuarios.
Este script combina todas las soluciones en un enfoque completo:
1. Configura la base de datos para usar UTC
2. Modifica los modelos para usar fechas sin zona horaria
3. Crea un parche para Tortoise ORM
"""
import os
import sys
import logging
import shutil
import subprocess
from datetime import datetime

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

def patch_model_files():
    """Parcha los archivos de modelos para usar fechas sin zona horaria"""
    logger.info("Parchando archivos de modelos...")
    
    # Lista de archivos a parchar con sus respectivos campos
    model_files = [
        {
            'path': os.path.join('app', 'infra', 'postgres', 'models', 'user.py'),
            'fields': ['created_at', 'updated_at']
        },
        {
            'path': os.path.join('app', 'infra', 'postgres', 'models', 'base.py'),
            'fields': ['created_at', 'updated_at']
        },
        # Agregar más modelos si es necesario
    ]
    
    success = True
    
    for model in model_files:
        model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), model['path'])
        
        if not os.path.exists(model_path):
            logger.warning(f"El archivo {model_path} no existe. Saltando.")
            continue
        
        try:
            # Crear copia de respaldo
            backup_path = f"{model_path}.bak"
            shutil.copy2(model_path, backup_path)
            logger.info(f"Copia de respaldo creada: {backup_path}")
            
            # Leer contenido
            with open(model_path, 'r') as f:
                content = f.read()
            
            # Modificar cada campo
            modified = False
            for field in model['fields']:
                if f'{field} = fields.DatetimeField(auto_now_add=True)' in content:
                    content = content.replace(
                        f'{field} = fields.DatetimeField(auto_now_add=True)',
                        f'{field} = fields.DatetimeField(auto_now_add=True, use_tz=False)'
                    )
                    modified = True
                
                if f'{field} = fields.DatetimeField(auto_now=True)' in content:
                    content = content.replace(
                        f'{field} = fields.DatetimeField(auto_now=True)',
                        f'{field} = fields.DatetimeField(auto_now=True, use_tz=False)'
                    )
                    modified = True
            
            if modified:
                # Escribir contenido modificado
                with open(model_path, 'w') as f:
                    f.write(content)
                logger.info(f"Archivo {model_path} parchado correctamente.")
            else:
                logger.warning(f"No se encontraron campos para modificar en {model_path}")
        
        except Exception as e:
            logger.error(f"Error al parchar {model_path}: {e}")
            # Restaurar backup
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, model_path)
                logger.info(f"Restaurada copia de respaldo para {model_path}")
            success = False
    
    return success

def create_tortoise_patch():
    """Crea un parche para Tortoise ORM"""
    logger.info("Creando parche para Tortoise ORM...")
    
    # Ruta del archivo de parche
    patch_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                           'app', 'infra', 'postgres')
    patch_file_path = os.path.join(patch_dir, 'timezone_patch.py')
    
    # Contenido del parche
    patch_content = """
# Archivo de parche para corregir problemas de zona horaria en Tortoise ORM
# Este archivo debe ser importado al inicio de la aplicación

import datetime
from tortoise import fields

# Guardar la implementación original de to_db_value
original_to_db_value = fields.DatetimeField.to_db_value

# Función para convertir fechas con zona horaria a fechas sin zona horaria
def convert_to_naive_datetime(value):
    if value is not None and hasattr(value, 'tzinfo') and value.tzinfo is not None:
        # Convertir a UTC y quitar la información de zona horaria
        value = value.replace(tzinfo=None)
    return value

# Parchar el método to_db_value de manera sincrónica
def patched_to_db_value(self, value, instance):
    # Convertir a fecha sin zona horaria
    value = convert_to_naive_datetime(value)
    
    # Llamar a la implementación original
    return original_to_db_value(self, value, instance)

# Aplicar el parche
fields.DatetimeField.to_db_value = patched_to_db_value

print("Parche de zona horaria aplicado a Tortoise ORM")
"""
    
    try:
        # Crear directorio si no existe
        os.makedirs(patch_dir, exist_ok=True)
        
        # Escribir archivo de parche
        with open(patch_file_path, 'w') as f:
            f.write(patch_content)
        
        logger.info(f"Archivo de parche creado: {patch_file_path}")
        
        # Modificar __init__.py para importar el parche
        init_file_path = os.path.join(patch_dir, '__init__.py')
        
        try:
            with open(init_file_path, 'r') as f:
                init_content = f.read()
        except FileNotFoundError:
            init_content = ""
        
        import_line = "\n# Importar parche de zona horaria\ntry:\n    from .timezone_patch import *\nexcept ImportError:\n    pass\n"
        
        if "from .timezone_patch import" not in init_content:
            with open(init_file_path, 'w') as f:
                f.write(init_content + import_line)
            logger.info(f"Archivo {init_file_path} modificado para importar el parche.")
        else:
            logger.info("El parche ya está importado en __init__.py")
        
        return True
    except Exception as e:
        logger.error(f"Error al crear el parche para Tortoise ORM: {e}")
        return False

def main():
    logger.info("Iniciando solución integral para el problema de zonas horarias...")
    
    # Paso 1: Configurar la base de datos
    db_fixed = fix_database_timezone()
    
    # Paso 2: Parchar los modelos
    models_patched = patch_model_files()
    
    # Paso 3: Crear parche para Tortoise ORM
    orm_patched = create_tortoise_patch()
    
    # Verificar resultados
    if db_fixed and models_patched and orm_patched:
        logger.info("¡Solución integral aplicada correctamente!")
        logger.info("Ahora debes reiniciar la aplicación para que los cambios surtan efecto.")
        logger.info("Comando recomendado: docker restart smartpay-db-api")
    else:
        logger.warning("La solución se aplicó parcialmente. Revisa los logs para más detalles.")
    
    logger.info("Proceso completado.")

if __name__ == "__main__":
    main()
