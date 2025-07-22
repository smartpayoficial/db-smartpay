import asyncio
from uuid import UUID

from tortoise import run_async

async def assign_default_store_admins():
    """Asigna admins por defecto a tiendas existentes"""
    from app.infra.postgres.models import Store, User
    
    # Buscar un usuario con rol de administrador
    admin = await User.filter(role__name="admin").first()
    
    if not admin:
        print("⚠️ No se encontró ningún usuario administrador")
        return
    
    # Actualizar tiendas sin admin
    updated = await Store.filter(admin=None).update(admin=admin)
    print(f"✅ Se asignó admin por defecto a {updated} tiendas")

# Para ejecutar con Tortoise
def init():
    run_async(assign_default_store_admins())
