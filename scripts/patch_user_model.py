#!/usr/bin/env python3
"""
Script para parchar directamente el modelo User y resolver el problema de zonas horarias.
Este script modifica el archivo del modelo User para que use fechas sin zona horaria.
"""
import os
import sys
import logging
import shutil
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def patch_user_model():
    """Parcha el modelo User para usar fechas sin zona horaria"""
    
    # Ruta del archivo del modelo User
    user_model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                  'app', 'infra', 'postgres', 'models', 'user.py')
    
    # Verificar si el archivo existe
    if not os.path.exists(user_model_path):
        logger.error(f"El archivo del modelo User no existe: {user_model_path}")
        return False
    
    try:
        # Crear una copia de respaldo
        backup_path = f"{user_model_path}.bak"
        shutil.copy2(user_model_path, backup_path)
        logger.info(f"Copia de respaldo creada: {backup_path}")
        
        # Leer el contenido actual
        with open(user_model_path, 'r') as f:
            content = f.read()
        
        # Buscar la definición de los campos created_at y updated_at
        if 'created_at = fields.DatetimeField(auto_now_add=True)' in content:
            # Reemplazar con campos que usan fechas sin zona horaria
            content = content.replace(
                'created_at = fields.DatetimeField(auto_now_add=True)',
                'created_at = fields.DatetimeField(auto_now_add=True, use_tz=False)'
            )
            content = content.replace(
                'updated_at = fields.DatetimeField(auto_now=True)',
                'updated_at = fields.DatetimeField(auto_now=True, use_tz=False)'
            )
            
            # Escribir el contenido modificado
            with open(user_model_path, 'w') as f:
                f.write(content)
            
            logger.info(f"Modelo User parchado correctamente: {user_model_path}")
            return True
        else:
            logger.error("No se encontró la definición de los campos created_at y updated_at")
            return False
    except Exception as e:
        logger.error(f"Error al parchar el modelo User: {e}")
        # Restaurar la copia de respaldo si existe
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, user_model_path)
            logger.info("Restaurada la copia de respaldo")
        return False

def patch_base_model():
    """Parcha el modelo base para usar fechas sin zona horaria"""
    
    # Ruta del archivo del modelo base
    base_model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                  'app', 'infra', 'postgres', 'models', 'base.py')
    
    # Verificar si el archivo existe
    if not os.path.exists(base_model_path):
        logger.error(f"El archivo del modelo base no existe: {base_model_path}")
        return False
    
    try:
        # Crear una copia de respaldo
        backup_path = f"{base_model_path}.bak"
        shutil.copy2(base_model_path, backup_path)
        logger.info(f"Copia de respaldo creada: {backup_path}")
        
        # Leer el contenido actual
        with open(base_model_path, 'r') as f:
            content = f.read()
        
        # Buscar la definición de los campos created_at y updated_at en el modelo base
        if 'created_at = fields.DatetimeField(auto_now_add=True)' in content:
            # Reemplazar con campos que usan fechas sin zona horaria
            content = content.replace(
                'created_at = fields.DatetimeField(auto_now_add=True)',
                'created_at = fields.DatetimeField(auto_now_add=True, use_tz=False)'
            )
            content = content.replace(
                'updated_at = fields.DatetimeField(auto_now=True)',
                'updated_at = fields.DatetimeField(auto_now=True, use_tz=False)'
            )
            
            # Escribir el contenido modificado
            with open(base_model_path, 'w') as f:
                f.write(content)
            
            logger.info(f"Modelo base parchado correctamente: {base_model_path}")
            return True
        else:
            logger.info("No se encontró la definición de los campos created_at y updated_at en el modelo base")
            return True  # No es un error si no se encuentra en el modelo base
    except Exception as e:
        logger.error(f"Error al parchar el modelo base: {e}")
        # Restaurar la copia de respaldo si existe
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, base_model_path)
            logger.info("Restaurada la copia de respaldo")
        return False

def main():
    logger.info("Iniciando el parchado de modelos...")
    
    # Parchar el modelo User
    user_patched = patch_user_model()
    
    # Parchar el modelo base
    base_patched = patch_base_model()
    
    if user_patched and base_patched:
        logger.info("Parchado completado correctamente.")
        logger.info("Ahora debes reiniciar la aplicación para que los cambios surtan efecto.")
    else:
        logger.error("No se pudo completar el parchado correctamente.")
    
    logger.info("Proceso completado.")

if __name__ == "__main__":
    main()
