"""
Script para eliminar un usuario SuperAdmin duplicado.
Este script lista los usuarios con rol SuperAdmin y permite eliminar uno de ellos.
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
    print("\nUsuarios SuperAdmin encontrados:")
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

async def delete_user(user_id):
    """Elimina un usuario por su ID."""
    conn = Tortoise.get_connection("default")
    
    query = """
    DELETE FROM "user" WHERE user_id = $1
    """
    
    try:
        await conn.execute_query(query, [user_id])
        print(f"\nUsuario con ID {user_id} eliminado exitosamente.")
        return True
    except Exception as e:
        print(f"\nError al eliminar usuario: {e}")
        return False

async def main():
    """Función principal."""
    try:
        print("Inicializando Tortoise ORM...")
        await init_tortoise()
        
        # Listar usuarios SuperAdmin
        superadmins = await list_superadmins()
        
        if not superadmins:
            return
        
        if len(superadmins) == 1:
            print("\nSolo hay un usuario SuperAdmin. No es necesario eliminar duplicados.")
            return
        
        # Solicitar al usuario que elija cuál eliminar
        print("\nPara eliminar un usuario, ejecute este script con el número de índice como argumento.")
        print("Ejemplo: python -m scripts.delete_duplicate_admin 2")
        
        # Si se proporciona un argumento, intentar eliminar ese usuario
        import sys
        if len(sys.argv) > 1:
            try:
                index = int(sys.argv[1])
                if 1 <= index <= len(superadmins):
                    user_to_delete = superadmins[index - 1]
                    confirm = input(f"\n¿Está seguro de eliminar al usuario {user_to_delete['username']} ({user_to_delete['full_name']})? (s/n): ")
                    if confirm.lower() == 's':
                        await delete_user(user_to_delete['user_id'])
                    else:
                        print("Operación cancelada.")
                else:
                    print(f"Índice inválido. Debe ser un número entre 1 y {len(superadmins)}.")
            except ValueError:
                print("Argumento inválido. Debe ser un número entero.")
    
    except Exception as e:
        print(f"Error en la ejecución: {e}")
    finally:
        await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(main())
