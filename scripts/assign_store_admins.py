#!/usr/bin/env python3
import asyncio
from uuid import UUID

from app.infra.postgres import init_db
from app.infra.postgres.models.store import Store
from app.infra.postgres.models.user import User

async def assign_default_admins():
    await init_db()
    
    # Buscar un usuario admin (ej: con rol de administrador)
    default_admin = await User.filter(role__name="admin").first()
    
    if not default_admin:
        print("No se encontró ningún usuario administrador")
        return
    
    # Actualizar todas las tiendas sin admin
    updated = await Store.filter(admin=None).update(admin=default_admin)
    print(f"Se actualizaron {updated} tiendas con admin por defecto")

if __name__ == "__main__":
    asyncio.run(assign_default_admins())
