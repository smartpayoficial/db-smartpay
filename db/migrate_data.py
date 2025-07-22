"""
Script para ejecutar migraciones de datos.
Se ejecuta después de las migraciones de esquema.
"""
import asyncio
from tortoise import run_async

from db.migrations import (
   0005_add_admin_to_store,
   0006_assign_store_admins
)

async def run_data_migrations():
    print("🏗️ Ejecutando migraciones de datos...")
    
    # Ejecutar migraciones en orden
    await run_async(0005_add_admin_to_store.init())
    await run_async(0006_assign_store_admins.init())
    
    print("✅ Migraciones de datos completadas")

if __name__ == "__main__":
    asyncio.run(run_data_migrations())
