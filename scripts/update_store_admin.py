"""
Script para actualizar la referencia del administrador en la tabla store.
"""

import asyncio
import os
from tortoise import Tortoise

# Configuración de la base de datos
DB_URL = os.getenv("POSTGRES_DATABASE_URL", "postgres://postgres:postgres@smartpay-db-v12:5432/smartpay")

async def init_tortoise():
    """Inicializa la conexión a Tortoise ORM."""
    await Tortoise.init(
        db_url=DB_URL,
        modules={"models": ["app.infra.postgres.models"]}
    )

async def list_stores_with_admins():
    """Lista todas las tiendas con sus administradores."""
    conn = Tortoise.get_connection("default")
    
    query = """
    SELECT s.id, s.nombre, s.admin_id, u.username, u.first_name, u.last_name
    FROM "store" s
    JOIN "user" u ON s.admin_id = u.user_id
    """
    
    result = await conn.execute_query(query)
    
    if not result[1]:
        print("No se encontraron tiendas.")
        return []
    
    stores = []
    print("\nTiendas encontradas:")
    print("-" * 100)
    print(f"{'#':<3} | {'Store ID':<36} | {'Nombre':<20} | {'Admin ID':<36} | {'Admin Username':<15} | {'Admin Nombre'}")
    print("-" * 100)
    
    for i, row in enumerate(result[1], 1):
        store_id, store_name, admin_id, username, first_name, last_name = row
        admin_name = f"{first_name} {last_name}"
        print(f"{i:<3} | {str(store_id):<36} | {store_name:<20} | {str(admin_id):<36} | {username:<15} | {admin_name}")
        stores.append({
            "index": i,
            "store_id": store_id,
            "store_name": store_name,
            "admin_id": admin_id,
            "admin_username": username,
            "admin_name": admin_name
        })
    
    return stores

async def update_store_admin(store_id, new_admin_id):
    """Actualiza el administrador de una tienda."""
    conn = Tortoise.get_connection("default")
    
    query = """
    UPDATE "store" SET admin_id = $1 WHERE id = $2
    """
    
    try:
        await conn.execute_query(query, [new_admin_id, store_id])
        print(f"\nTienda con ID {store_id} actualizada exitosamente con nuevo admin ID {new_admin_id}.")
        return True
    except Exception as e:
        print(f"\nError al actualizar tienda: {e}")
        return False

async def list_superadmins():
    """Lista todos los usuarios con rol SuperAdmin."""
    conn = Tortoise.get_connection("default")
    
    query = """
    SELECT u.user_id, u.username, u.first_name, u.last_name, u.email, u.created_at, r.name as role_name
    FROM "user" u
    JOIN "role" r ON u.role_id = r.role_id
    WHERE r.name = 'SuperAdmin'
    """
    
    result = await conn.execute_query(query)
    
    if not result[1]:
        print("No se encontraron usuarios SuperAdmin.")
        return []
    
    superadmins = []
    print("\nUsuarios SuperAdmin disponibles:")
    print("-" * 80)
    print(f"{'#':<3} | {'User ID':<36} | {'Username':<15} | {'Nombre':<20} | {'Email':<25} | {'Creado'}")
    print("-" * 80)
    
    for i, row in enumerate(result[1], 1):
        user_id, username, first_name, last_name, email, created_at, role_name = row
        full_name = f"{first_name} {last_name}"
        print(f"{i:<3} | {str(user_id):<36} | {username:<15} | {full_name:<20} | {email:<25} | {created_at}")
        superadmins.append({
            "index": i,
            "user_id": user_id,
            "username": username,
            "full_name": full_name,
            "email": email,
            "created_at": created_at
        })
    
    return superadmins

async def main():
    """Función principal."""
    try:
        print("Inicializando Tortoise ORM...")
        await init_tortoise()
        
        # Listar tiendas con sus administradores
        stores = await list_stores_with_admins()
        
        if not stores:
            print("No hay tiendas para actualizar.")
            return
        
        # Listar usuarios SuperAdmin disponibles
        superadmins = await list_superadmins()
        
        if not superadmins:
            print("No hay usuarios SuperAdmin disponibles.")
            return
        
        # Si se proporcionan argumentos, intentar actualizar la tienda
        import sys
        if len(sys.argv) > 2:
            try:
                store_index = int(sys.argv[1])
                admin_index = int(sys.argv[2])
                
                if 1 <= store_index <= len(stores) and 1 <= admin_index <= len(superadmins):
                    store = stores[store_index - 1]
                    admin = superadmins[admin_index - 1]
                    
                    print(f"\nActualizando tienda '{store['store_name']}' para usar el admin '{admin['username']}' ({admin['full_name']})...")
                    await update_store_admin(store['store_id'], admin['user_id'])
                else:
                    print(f"Índices inválidos. Store index debe estar entre 1 y {len(stores)}, y admin index entre 1 y {len(superadmins)}.")
            except ValueError:
                print("Argumentos inválidos. Deben ser números enteros.")
        else:
            print("\nPara actualizar una tienda, ejecute este script con el número de índice de la tienda y el número de índice del admin.")
            print("Ejemplo: python -m scripts.update_store_admin 1 1")
    
    except Exception as e:
        print(f"Error en la ejecución: {e}")
    finally:
        await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(main())
