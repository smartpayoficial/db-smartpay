#!/usr/bin/env python3
"""
Script para crear una restricción de unicidad compuesta entre store_id y dni en la aplicación SmartPay.

Este script:
1. Modifica el modelo User en Tortoise ORM para agregar un Meta.unique_together
2. Ejecuta una migración SQL para añadir la restricción UNIQUE compuesta en la base de datos
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

# SQL para agregar la restricción de unicidad compuesta
SQL_ADD_UNIQUE = """
-- Agregar la restricción UNIQUE compuesta entre store_id y dni en la tabla user
ALTER TABLE "user" ADD CONSTRAINT user_store_id_dni_key UNIQUE (store_id, dni);

-- Nota: Esta restricción permite DNIs duplicados cuando store_id es NULL
-- Si se requiere unicidad para usuarios sin tienda, se necesitaría una lógica adicional
"""

async def modify_user_model():
    """Modifica el modelo User para agregar Meta.unique_together para store_id y dni."""
    try:
        # Leer el archivo
        with open(USER_MODEL_PATH, "r") as file:
            content = file.readlines()
        
        # Buscar la clase User y agregar Meta class
        new_content = []
        in_user_class = False
        meta_added = False
        
        for line in content:
            new_content.append(line)
            
            if line.strip() == "class User(Model):":
                in_user_class = True
                continue
                
            if in_user_class and not meta_added and line.strip().startswith("user_id = "):
                # Agregar la clase Meta después de la primera línea de la clase User
                indent = line.split("user_id")[0]  # Obtener la indentación
                meta_lines = [
                    f"\n{indent}class Meta:\n",
                    f"{indent}    unique_together = (('store', 'dni'),)\n"
                ]
                new_content.extend(meta_lines)
                meta_added = True
        
        # Escribir el archivo modificado
        with open(USER_MODEL_PATH, "w") as file:
            file.writelines(new_content)
        
        logger.info("✅ Modelo User modificado correctamente con unique_together")
        return True
    except Exception as e:
        logger.error(f"❌ Error al modificar el modelo User: {str(e)}")
        return False

async def execute_sql():
    """Ejecuta el SQL para agregar la restricción UNIQUE compuesta en la base de datos usando Docker."""
    try:
        # Crear archivo SQL temporal con el comando
        sql_file_path = BASE_DIR / "scripts" / "temp_add_unique_constraint.sql"
        with open(sql_file_path, "w") as file:
            file.write(SQL_ADD_UNIQUE)
        
        # Intentar encontrar el nombre del contenedor de PostgreSQL
        logger.info("Buscando el contenedor de PostgreSQL...")
        find_container_cmd = "docker ps | grep postgres | awk '{print $1}'"
        container_id = os.popen(find_container_cmd).read().strip()
        
        if not container_id:
            logger.warning("No se encontró un contenedor de PostgreSQL en ejecución.")
            logger.info("Intentando usar el contenedor 'db-smartpay-db-1'...")
            container_id = "db-smartpay-db-1"
        
        # Copiar el archivo SQL al contenedor
        copy_cmd = f"docker cp {sql_file_path} {container_id}:/tmp/add_unique_constraint.sql"
        logger.info(f"Copiando archivo SQL al contenedor: {container_id}")
        copy_result = os.system(copy_cmd)
        
        if copy_result != 0:
            logger.error(f"❌ Error al copiar el archivo SQL al contenedor. Código: {copy_result}")
            return False
        
        # Ejecutar el SQL en el contenedor
        logger.info("Ejecutando SQL para agregar restricción UNIQUE compuesta...")
        exec_cmd = f"docker exec {container_id} psql -U postgres -d smartpay -f /tmp/add_unique_constraint.sql"
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
    logger.info("Iniciando proceso para crear restricción de unicidad compuesta entre store_id y dni...")
    
    # Modificar el modelo User
    model_modified = await modify_user_model()
    
    # Ejecutar SQL para agregar la restricción UNIQUE compuesta
    sql_executed = await execute_sql()
    
    # Verificar resultados
    if model_modified and sql_executed:
        logger.info("✅ Proceso completado con éxito. La restricción de unicidad compuesta ha sido agregada.")
        logger.info("⚠️ IMPORTANTE: Recuerde reiniciar la API para aplicar los cambios en el modelo.")
    else:
        logger.error("❌ El proceso no se completó correctamente. Revise los errores anteriores.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
