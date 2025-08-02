#!/usr/bin/env python3
"""
Script consolidado para aplicar en VPS:
1. Eliminar la restricción de unicidad del campo DNI
2. Crear una restricción de unicidad compuesta entre store_id y dni

Este script está diseñado para ejecutarse directamente en el servidor VPS.
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

# SQL para ejecutar ambos cambios
SQL_COMMANDS = """
-- Eliminar la restricción UNIQUE del campo dni en la tabla user
ALTER TABLE "user" DROP CONSTRAINT IF EXISTS user_dni_key;

-- Agregar la restricción UNIQUE compuesta entre store_id y dni en la tabla user
ALTER TABLE "user" ADD CONSTRAINT user_store_id_dni_key UNIQUE (store_id, dni);
"""

async def modify_user_model():
    """Modifica el modelo User para quitar unique=True del campo dni y agregar unique_together."""
    try:
        # Leer el archivo
        with open(USER_MODEL_PATH, "r") as file:
            content = file.read()
        
        # Reemplazar la definición del campo dni
        modified_content = content.replace(
            'dni = fields.CharField(max_length=16, unique=True)',
            'dni = fields.CharField(max_length=16)'
        )
        
        # Escribir el archivo modificado temporalmente
        with open(USER_MODEL_PATH, "w") as file:
            file.write(modified_content)
        
        # Ahora leemos el archivo modificado para agregar Meta class
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
        
        # Escribir el archivo con ambas modificaciones
        with open(USER_MODEL_PATH, "w") as file:
            file.writelines(new_content)
        
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
    """Ejecuta el SQL para aplicar los cambios en la base de datos."""
    try:
        # Crear archivo SQL temporal
        sql_file_path = "/tmp/dni_store_constraint.sql"
        with open(sql_file_path, "w") as file:
            file.write(SQL_COMMANDS)
        
        # Determinar el método de conexión a la base de datos
        # Primero intentamos con Docker
        logger.info("Intentando ejecutar SQL usando Docker...")
        find_container_cmd = "docker ps | grep postgres | awk '{print $1}'"
        container_id = os.popen(find_container_cmd).read().strip()
        
        if container_id:
            # Usar Docker
            logger.info(f"Usando contenedor Docker: {container_id}")
            copy_cmd = f"docker cp {sql_file_path} {container_id}:/tmp/dni_store_constraint.sql"
            os.system(copy_cmd)
            exec_cmd = f"docker exec {container_id} psql -U postgres -d smartpay -f /tmp/dni_store_constraint.sql"
            result = os.system(exec_cmd)
        else:
            # Intentar con psql directo
            logger.info("No se encontró contenedor Docker, intentando con psql directo...")
            # Obtener variables de entorno para la conexión
            db_host = os.environ.get("POSTGRES_HOST", "localhost")
            db_port = os.environ.get("POSTGRES_PORT", "5432")
            db_name = os.environ.get("POSTGRES_DB", "smartpay")
            db_user = os.environ.get("POSTGRES_USER", "postgres")
            db_password = os.environ.get("POSTGRES_PASSWORD", "postgres")
            
            # Construir comando psql
            psql_cmd = f"PGPASSWORD={db_password} psql -h {db_host} -p {db_port} -U {db_user} -d {db_name} -f {sql_file_path}"
            result = os.system(psql_cmd)
        
        # Eliminar archivo temporal
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
    logger.info("Iniciando proceso para modificar restricciones de DNI y store_id...")
    
    # Modificar el modelo User
    model_modified = await modify_user_model()
    
    # Modificar el router de autenticación
    router_modified = await modify_auth_router()
    
    # Ejecutar SQL para aplicar los cambios en la base de datos
    sql_executed = await execute_sql()
    
    # Verificar resultados
    if model_modified and router_modified and sql_executed:
        logger.info("✅ Proceso completado con éxito.")
        logger.info("⚠️ IMPORTANTE: Recuerde reiniciar la API para aplicar los cambios en el modelo.")
        
        # Instrucciones para reiniciar el servicio
        logger.info("\nPara reiniciar el servicio de la API, ejecute:")
        logger.info("  sudo systemctl restart smartpay-api")
        logger.info("  # o el comando correspondiente según su configuración")
    else:
        logger.error("❌ El proceso no se completó correctamente. Revise los errores anteriores.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
