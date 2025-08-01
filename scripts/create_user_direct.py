"""
Script para crear un usuario directamente en la base de datos usando Tortoise ORM.
Evita los problemas de fechas con timezone al crear los usuarios directamente
en lugar de usar el API.
"""

import asyncio
import os
import datetime
from tortoise import Tortoise
from passlib.context import CryptContext

# Configuración de la base de datos
DB_URL = os.getenv("POSTGRES_DATABASE_URL", "postgres://postgres:postgres@smartpay-db-v12:5432/smartpay")

# Configuración para hash de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configurar zona horaria en Python
os.environ['TZ'] = 'UTC'
try:
    import time
    time.tzset()
except AttributeError:
    pass

async def init_tortoise():
    """Inicializa la conexión a Tortoise ORM."""
    await Tortoise.init(
        db_url=DB_URL,
        modules={"models": ["app.infra.postgres.models"]}
    )

async def create_superadmin_user(city_id, role_id):
    """Crea un usuario superadmin directamente en la base de datos."""
    # Obtener conexión
    conn = Tortoise.get_connection("default")
    
    # Generar hash de contraseña
    hashed_password = pwd_context.hash("secret")
    
    # Fecha actual en UTC sin zona horaria
    now = datetime.datetime.utcnow()
    
    # Crear usuario directamente con SQL para evitar problemas de timezone
    query = """
    INSERT INTO "user" (
        city_id, dni, first_name, middle_name, last_name, second_last_name,
        email, phone, address, username, password, role_id, state, created_at, updated_at
    ) VALUES (
        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15
    ) RETURNING user_id
    """
    
    values = [
        city_id,                 # city_id
        "10000000",              # dni
        "Admin",                 # first_name
        "",                      # middle_name
        "Super",                 # last_name
        "",                      # second_last_name
        "admin@smartpay.com",    # email
        "1234567890",            # phone
        "Admin Address",         # address
        "admin",                 # username
        hashed_password,         # password
        role_id,                 # role_id
        "Active",                # state
        now,                     # created_at
        now                      # updated_at
    ]
    
    try:
        result = await conn.execute_query(query, values)
        user_id = result[1][0][0]
        print(f"Usuario superadmin creado con ID: {user_id}")
        return user_id
    except Exception as e:
        print(f"Error al crear usuario superadmin: {e}")
        raise

async def create_admin_user(city_id, role_id, store_id=None):
    """Crea un usuario admin directamente en la base de datos."""
    # Obtener conexión
    conn = Tortoise.get_connection("default")
    
    # Generar hash de contraseña
    hashed_password = pwd_context.hash("secret")
    
    # Fecha actual en UTC sin zona horaria
    now = datetime.datetime.utcnow()
    
    # Crear usuario directamente con SQL para evitar problemas de timezone
    query = """
    INSERT INTO "user" (
        city_id, dni, first_name, middle_name, last_name, second_last_name,
        email, phone, address, username, password, role_id, state, created_at, updated_at, store_id
    ) VALUES (
        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16
    ) RETURNING user_id
    """
    
    values = [
        city_id,                 # city_id
        "20000000",              # dni
        "Admin",                 # first_name
        "",                      # middle_name
        "Store",                 # last_name
        "",                      # second_last_name
        "admin_store@smartpay.com", # email
        "0987654321",            # phone
        "Store Admin Address",   # address
        "admin_store",           # username
        hashed_password,         # password
        role_id,                 # role_id
        "Active",                # state
        now,                     # created_at
        now,                     # updated_at
        store_id                 # store_id
    ]
    
    try:
        result = await conn.execute_query(query, values)
        user_id = result[1][0][0]
        print(f"Usuario admin creado con ID: {user_id}")
        return user_id
    except Exception as e:
        print(f"Error al crear usuario admin: {e}")
        raise

async def create_store(admin_id=None, country_id=None):
    """Crea una tienda directamente en la base de datos."""
    # Obtener conexión
    conn = Tortoise.get_connection("default")
    
    # Fecha actual en UTC sin zona horaria
    now = datetime.datetime.utcnow()
    
    # Crear tienda directamente con SQL
    query = """
    INSERT INTO "store" (
        nombre, tokens_disponibles, plan, admin_id, created_at, updated_at, country_id
    ) VALUES (
        $1, $2, $3, $4, $5, $6, $7
    ) RETURNING id
    """
    
    values = [
        "Tienda Principal",      # nombre
        1000,                    # tokens_disponibles
        "Premium",               # plan
        admin_id,                # admin_id
        now,                     # created_at
        now,                     # updated_at
        country_id               # country_id
    ]
    
    try:
        result = await conn.execute_query(query, values)
        store_id = result[1][0][0]
        print(f"Tienda creada con ID: {store_id}")
        return store_id
    except Exception as e:
        print(f"Error al crear tienda: {e}")
        raise

async def get_first_city_id():
    """Obtiene el ID de la primera ciudad en la base de datos."""
    conn = Tortoise.get_connection("default")
    result = await conn.execute_query("SELECT city_id FROM city LIMIT 1")
    if result and result[1]:
        return result[1][0][0]
    return None

async def get_first_country_id():
    """Obtiene el ID del primer país en la base de datos."""
    conn = Tortoise.get_connection("default")
    result = await conn.execute_query("SELECT country_id FROM country LIMIT 1")
    if result and result[1]:
        return result[1][0][0]
    return None

async def get_role_id_by_name(role_name):
    """Obtiene el ID de un rol por su nombre."""
    conn = Tortoise.get_connection("default")
    result = await conn.execute_query(f"SELECT role_id FROM role WHERE name = '{role_name}'")
    if result and result[1]:
        return result[1][0][0]
    return None

async def main():
    """Función principal para crear usuarios y tienda."""
    try:
        print("Inicializando Tortoise ORM...")
        await init_tortoise()
        
        # Obtener IDs necesarios
        city_id = await get_first_city_id()
        country_id = await get_first_country_id()
        superadmin_role_id = await get_role_id_by_name("SuperAdmin")
        admin_role_id = await get_role_id_by_name("Admin")
        
        if not city_id:
            print("Error: No se encontró ninguna ciudad en la base de datos.")
            return
        
        if not country_id:
            print("Error: No se encontró ningún país en la base de datos.")
            return
        
        if not superadmin_role_id:
            print("Error: No se encontró el rol SuperAdmin en la base de datos.")
            return
        
        if not admin_role_id:
            print("Error: No se encontró el rol Admin en la base de datos.")
            return
        
        print(f"City ID: {city_id}, Country ID: {country_id}")
        print(f"SuperAdmin Role ID: {superadmin_role_id}, Admin Role ID: {admin_role_id}")
        
        # Crear superadmin
        superadmin_id = await create_superadmin_user(city_id, superadmin_role_id)
        
        # Crear tienda
        store_id = await create_store(superadmin_id, country_id)
        
        # Crear admin de tienda
        admin_id = await create_admin_user(city_id, admin_role_id, store_id)
        
        # Actualizar tienda con el admin_id si es necesario
        if not superadmin_id:
            conn = Tortoise.get_connection("default")
            await conn.execute_query(f"UPDATE store SET admin_id = {admin_id} WHERE id = {store_id}")
            print(f"Tienda actualizada con admin_id: {admin_id}")
        
        print("Usuarios y tienda creados exitosamente.")
    
    except Exception as e:
        print(f"Error en la ejecución: {e}")
    finally:
        await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(main())
