#!/usr/bin/env python3
"""
Script para eliminar la restricción de unicidad del campo DNI en la aplicación SmartPay.

Este script:
1. Modifica el modelo User en Tortoise ORM para quitar unique=True
2. Ejecuta una migración SQL para eliminar la restricción UNIQUE en la base de datos
3. Modifica el router de autenticación para eliminar la validación de DNI único
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Rutas de archivos a modificar
BASE_DIR = Path(__file__).parent.parent
USER_MODEL_PATH = BASE_DIR / "app" / "infra" / "postgres" / "models" / "user.py"
AUTH_ROUTER_PATH = BASE_DIR / "app" / "api" / "routers" / "internal_auth.py"

# SQL para eliminar la restricción de unicidad
SQL_REMOVE_UNIQUE = """
-- Eliminar la restricción UNIQUE del campo dni en la tabla user
ALTER TABLE "user" DROP CONSTRAINT IF EXISTS user_dni_key;
"""

async def modify_user_model():
    """Modifica el modelo User para eliminar unique=True del campo dni."""
    try:
        # Leer el archivo
        with open(USER_MODEL_PATH, "r") as file:
            content = file.read()
        
        # Reemplazar la definición del campo dni
        modified_content = content.replace(
            'dni = fields.CharField(max_length=16, unique=True)',
            'dni = fields.CharField(max_length=16)'
        )
        
        # Escribir el archivo modificado
        with open(USER_MODEL_PATH, "w") as file:
            file.write(modified_content)
        
        logger.info("✅ Modelo User modificado correctamente")
        return True
    except Exception as e:
        logger.error(f"❌ Error al modificar el modelo User: {str(e)}")
        return False

async def modify_auth_router():
    """Modifica el router de autenticación para eliminar la validación de DNI único."""
    try:
        # Leer el archivo
        with open(AUTH_ROUTER_PATH, "r") as file:
            content = file.readlines()
        
        # Identificar y eliminar las líneas de validación de DNI único
        new_content = []
        skip_next_lines = 0
        
        for i, line in enumerate(content):
            if skip_next_lines > 0:
                skip_next_lines -= 1
                continue
                
            if "exists = await User.filter(dni=new_user.dni).exists()" in line:
                # Saltar esta línea y las dos siguientes (if exists y raise HTTPException)
                skip_next_lines = 2
                continue
                
            new_content.append(line)
        
        # Escribir el archivo modificado
        with open(AUTH_ROUTER_PATH, "w") as file:
            file.writelines(new_content)
        
        logger.info("✅ Router de autenticación modificado correctamente")
        return True
    except Exception as e:
        logger.error(f"❌ Error al modificar el router de autenticación: {str(e)}")
        return False

async def execute_sql():
    """Ejecuta el SQL para eliminar la restricción UNIQUE en la base de datos usando Docker."""
    try:
        # Crear archivo SQL temporal con el comando
        sql_file_path = BASE_DIR / "scripts" / "temp_remove_dni_unique.sql"
        with open(sql_file_path, "w") as file:
            file.write(SQL_REMOVE_UNIQUE)
        
        # Intentar encontrar el nombre del contenedor de PostgreSQL
        logger.info("Buscando el contenedor de PostgreSQL...")
        find_container_cmd = "docker ps | grep postgres | awk '{print $1}'"
        container_id = os.popen(find_container_cmd).read().strip()
        
        if not container_id:
            logger.warning("No se encontró un contenedor de PostgreSQL en ejecución.")
            logger.info("Intentando usar el contenedor 'db-smartpay-db-1'...")
            container_id = "db-smartpay-db-1"
        
        # Copiar el archivo SQL al contenedor
        copy_cmd = f"docker cp {sql_file_path} {container_id}:/tmp/remove_dni_unique.sql"
        logger.info(f"Copiando archivo SQL al contenedor: {container_id}")
        copy_result = os.system(copy_cmd)
        
        if copy_result != 0:
            logger.error(f"❌ Error al copiar el archivo SQL al contenedor. Código: {copy_result}")
            return False
        
        # Ejecutar el SQL en el contenedor
        logger.info("Ejecutando SQL para eliminar restricción UNIQUE...")
        exec_cmd = f"docker exec {container_id} psql -U postgres -d smartpay -f /tmp/remove_dni_unique.sql"
        result = os.system(exec_cmd)
        
        # Eliminar archivo temporal local
        os.remove(sql_file_path)
        
        if result == 0:
            logger.info("✅ SQL ejecutado correctamente")
            return True
        else:
            logger.error(f"❌ Error al ejecutar SQL. Código de salida: {result}")
            return False
    except Exception as e:
        logger.error(f"❌ Error al ejecutar SQL: {str(e)}")
        return False

async def main():
    """Función principal que ejecuta todas las tareas."""
    logger.info("Iniciando proceso para eliminar la unicidad del campo DNI...")
    
    # Modificar el modelo User
    model_modified = await modify_user_model()
    
    # Modificar el router de autenticación
    router_modified = await modify_auth_router()
    
    # Ejecutar SQL para eliminar la restricción UNIQUE
    sql_executed = await execute_sql()
    
    # Verificar resultados
    if model_modified and router_modified and sql_executed:
        logger.info("✅ Proceso completado con éxito. La restricción de unicidad del DNI ha sido eliminada.")
        logger.info("⚠️ IMPORTANTE: Recuerde reiniciar la API para aplicar los cambios en el modelo.")
    else:
        logger.error("❌ El proceso no se completó correctamente. Revise los errores anteriores.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
