#!/usr/bin/env python3
"""
Script para corregir el error de sintaxis en el archivo __init__.py de Tortoise ORM.
"""
import os
import logging
import subprocess

# Configurar logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_init_file():
    """Corrige el archivo __init__.py de Tortoise ORM"""
    try:
        # Crear un archivo temporal con el contenido correcto
        with open("init_fix.py", "w") as f:
            f.write("""
# Importar parche de zona horaria
try:
    import tortoise_patch
except ImportError:
    pass
""")
        
        # Copiar el archivo al contenedor
        result = subprocess.run(
            "docker cp init_fix.py smartpay-db-api:/tmp/",
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Ejecutar comando para reemplazar la línea problemática
        cmd = """docker exec smartpay-db-api bash -c "sed -i '/try:\\\\n/d' /usr/local/lib/python3.8/site-packages/tortoise/__init__.py && cat /tmp/init_fix.py >> /usr/local/lib/python3.8/site-packages/tortoise/__init__.py" """
        
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
    logger.info("Iniciando corrección del archivo __init__.py...")
    
    # Corregir el archivo __init__.py
    if not fix_init_file():
        logger.error("No se pudo corregir el archivo __init__.py. Abortando.")
        return
    
    # Reiniciar el contenedor
    if not restart_container():
        logger.error("No se pudo reiniciar el contenedor. Abortando.")
        return
    
    logger.info("Proceso completado correctamente.")
    logger.info("Ahora puedes probar la creación de usuarios nuevamente.")

if __name__ == "__main__":
    main()
