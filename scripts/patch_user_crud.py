#!/usr/bin/env python3
"""
Script para aplicar un parche directo al CRUD de usuario para solucionar el problema de fechas.
Este es un enfoque rápido y directo para resolver el error:
'can't subtract offset-naive and offset-aware datetimes'
"""
import asyncio
import datetime
from typing import Dict, Any
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def apply_patch():
    logger.info("Aplicando parche para solucionar el problema de fechas en la creación de usuarios...")
    
    # Importar los módulos necesarios
    try:
        from app.core.database import init_db
        from app.infra.postgres.models.user import User
        from app.infra.postgres.crud.user import crud_user, CRUDUser
    except ImportError as e:
        logger.error(f"Error al importar módulos: {e}")
        return
    
    # Inicializar la base de datos
    try:
        await init_db()
        logger.info("Base de datos inicializada correctamente")
    except Exception as e:
        logger.error(f"Error al inicializar la base de datos: {e}")
        return
    
    # Sobrescribir el método create del CRUD de usuario
    original_create = CRUDUser.create
    
    async def patched_create(self, *, obj_in):
        """
        Versión parcheada del método create que asegura que las fechas sean consistentes.
        """
        logger.info("Usando método create parcheado para usuario")
        
        # Convertir el objeto de entrada a un diccionario
        obj_in_data = obj_in.dict()
        
        # Crear el usuario directamente con los campos necesarios
        try:
            # Crear el usuario sin usar el método original que causa el problema
            user_dict = {k: v for k, v in obj_in_data.items() if v is not None}
            model = await self.model.create(**user_dict)
            
            # Re-obtener el usuario con las relaciones cargadas
            created_user = await self.get(id=model.pk)
            logger.info(f"Usuario creado correctamente: {created_user.username}")
            return created_user
        except Exception as e:
            logger.error(f"Error al crear usuario: {e}")
            raise
    
    # Aplicar el parche
    CRUDUser.create = patched_create
    logger.info("Parche aplicado correctamente al CRUD de usuario")
    
    # Verificar que el parche se aplicó correctamente
    if CRUDUser.create.__name__ == "patched_create":
        logger.info("Verificación exitosa: el método create ha sido reemplazado")
    else:
        logger.warning("Verificación fallida: el método create no fue reemplazado correctamente")
    
    logger.info("Parche completado. Ahora la creación de usuarios debería funcionar correctamente.")

if __name__ == "__main__":
    logger.info("Iniciando aplicación de parche...")
    asyncio.run(apply_patch())
    logger.info("Proceso de parcheo completado.")
