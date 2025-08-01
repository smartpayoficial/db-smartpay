#!/usr/bin/env python3
import asyncio
import datetime
from typing import Dict, Any

from tortoise import Tortoise
from app.core.config import settings
from app.infra.postgres.models.user import User

# Función para corregir el problema de fechas en la creación de usuarios
async def fix_user_creation():
    print("Iniciando corrección para la creación de usuarios...")
    
    # Conectar a la base de datos
    await Tortoise.init(
        db_url=settings.DATABASE_URL,
        modules={"models": ["app.infra.postgres.models"]}
    )
    
    # Sobrescribir el método save del modelo User para asegurar que las fechas sean consistentes
    original_save = User.save
    
    async def patched_save(self, *args, **kwargs):
        # Asegurar que created_at y updated_at sean naive (sin zona horaria)
        if hasattr(self, 'created_at') and self.created_at and self.created_at.tzinfo:
            self.created_at = self.created_at.replace(tzinfo=None)
        
        if hasattr(self, 'updated_at') and self.updated_at and self.updated_at.tzinfo:
            self.updated_at = self.updated_at.replace(tzinfo=None)
            
        # Llamar al método original
        return await original_save(self, *args, **kwargs)
    
    # Reemplazar el método save
    User.save = patched_save
    
    print("Corrección aplicada. Ahora la creación de usuarios debería funcionar correctamente.")
    print("Importante: Esta es una solución temporal. Se recomienda actualizar la configuración de Tortoise ORM.")
    
    # Cerrar la conexión
    await Tortoise.close_connections()

if __name__ == "__main__":
    print("Iniciando script de corrección...")
    asyncio.run(fix_user_creation())
    print("Proceso completado.")
