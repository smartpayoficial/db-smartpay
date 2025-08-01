"""Script mejorado para sembrar datos iniciales en la base de datos.

Este script combina la creación de entidades geográficas y roles mediante la API,
pero crea usuarios directamente en la base de datos para evitar problemas de zona horaria.
"""

import asyncio
import os
import datetime
import uuid
import httpx
from tortoise import Tortoise
from passlib.context import CryptContext

# Configuración
BASE_URL = "http://localhost:8002"
API_PREFIX = "/api/v1"
DB_URL = os.getenv("POSTGRES_DATABASE_URL", "postgres://postgres:postgres@smartpay-db-v12:5432/smartpay")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configurar zona horaria
os.environ['TZ'] = 'UTC'
try:
    import time
    time.tzset()
except AttributeError:
    pass

# Funciones de ayuda para API
async def _request(client, method, endpoint, **kwargs):
    """Helper function to make API requests and handle responses."""
    url = f"{BASE_URL}{API_PREFIX}{endpoint}"
    try:
        response = await client.request(method, url, timeout=10.0, **kwargs)
        if response.status_code in {200, 201}:
            print(f"    -> {method.upper()} {endpoint} {response.status_code} OK")
            return response.json()
        if response.status_code in {400, 409} and method.lower() == "post":
            list_resp = await client.get(f"{BASE_URL}{API_PREFIX}{endpoint}", timeout=10.0)
            if list_resp.status_code == 200 and list_resp.json():
                print(f"    -> {method.upper()} {endpoint} {response.status_code}: Already exists. Using first record.")
                return list_resp.json()[0]
        print(f"    -> {method.upper()} {endpoint} {response.status_code}: {response.text}")
    except Exception as exc:
        print(f"    !! Error en {method.upper()} {url}: {exc}")
    return None

# Funciones para crear usuarios directamente en la base de datos
async def init_tortoise():
    await Tortoise.init(db_url=DB_URL, modules={"models": ["app.infra.postgres.models"]})

async def create_user(city_id, role_id, dni, first_name, last_name, email, phone, username, store_id=None):
    conn = Tortoise.get_connection("default")
    hashed_password = pwd_context.hash("secret")
    now = datetime.datetime.utcnow()
    user_id = str(uuid.uuid4())
    
    query = """
    INSERT INTO "user" (
        user_id, city_id, dni, first_name, last_name, email, prefix, phone, 
        address, username, password, role_id, state, created_at, updated_at, store_id
    ) VALUES (
        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16
    ) RETURNING user_id
    """
    
    values = [
        user_id, city_id, dni, first_name, last_name, email, "+51", phone,
        f"Dirección de {first_name}", username, hashed_password, 
        role_id, "Active", now, now, store_id
    ]
    
    try:
        result = await conn.execute_query(query, values)
        user_id = result[1][0][0]
        print(f"    -> Usuario {username} creado con ID: {user_id}")
        return user_id
    except Exception as e:
        print(f"    !! Error al crear usuario {username}: {e}")
        return None

async def create_store(name, tokens, plan, admin_id, country_id):
    conn = Tortoise.get_connection("default")
    now = datetime.datetime.utcnow()
    store_id = str(uuid.uuid4())
    
    query = """
    INSERT INTO "store" (id, nombre, tokens_disponibles, plan, admin_id, created_at, updated_at, country_id)
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8) RETURNING id
    """
    
    values = [store_id, name, tokens, plan, admin_id, now, now, country_id]
    
    try:
        result = await conn.execute_query(query, values)
        store_id = result[1][0][0]
        print(f"    -> Tienda {name} creada con ID: {store_id}")
        return store_id
    except Exception as e:
        print(f"    !! Error al crear tienda {name}: {e}")
        return None

# Función principal de siembra
async def seed():
    async with httpx.AsyncClient() as client:
        print("\n--- Iniciando siembra de datos mejorada ---")
        
        # --- Geografía ---
        print("\nSeeding country…")
        country = await _request(client, "post", "/countries/", json={"name": "Peru", "code": "PE"})
        if not country:
            print("No se pudo sembrar el país, abortando.")
            return
        country_id = country["country_id"]
        
        print("Seeding region…")
        region = await _request(client, "post", "/regions/", json={"name": "Lima", "country_id": country_id})
        if not region:
            print("No se pudo sembrar la región, abortando.")
            return
        region_id = region["region_id"]
        
        print("Seeding city…")
        city = await _request(client, "post", "/cities/", json={"name": "Lima", "region_id": region_id, "state": "Active"})
        if not city:
            print("No se pudo sembrar la ciudad, abortando.")
            return
        city_id = city["city_id"]
        
        # --- Roles ---
        print("\nSeeding roles…")
        roles = {
            "SuperAdmin": "Administrador de sistema principal",
            "Admin": "Administrador de plataforma",
            "Vendedor": "Usuario vendedor",
            "Cliente": "Usuario final o cliente",
            "Device": "Rol para el dispositivo"
        }
        
        role_ids = {}
        for name, desc in roles.items():
            role = await _request(client, "post", "/roles/", json={"name": name, "description": desc})
            if role:
                role_ids[name] = role["role_id"]
        
        if len(role_ids) != len(roles):
            print("No se pudieron sembrar todos los roles, abortando.")
            return
        
        # --- Inicializar Tortoise para crear usuarios directamente ---
        print("\nInicializando conexión directa a la base de datos...")
        await init_tortoise()
        
        # --- Usuarios ---
        print("\nSeeding users directamente en la base de datos...")
        
        # SuperAdmin
        superadmin_id = await create_user(
            city_id, role_ids["SuperAdmin"], "10000000", "Admin", "Maestro", 
            "superadmin@example.com", "900000000", "superadmin"
        )
        
        if not superadmin_id:
            print("No se pudo crear el usuario SuperAdmin, abortando.")
            await Tortoise.close_connections()
            return
        
        # Tienda
        print("\nCreando tienda...")
        store_id = await create_store("Tienda Principal", 1000, "Premium", superadmin_id, country_id)
        
        if not store_id:
            print("No se pudo crear la tienda, abortando.")
            await Tortoise.close_connections()
            return
        
        # Admin de tienda
        admin_id = await create_user(
            city_id, role_ids["Admin"], "20000000", "Admin", "Tienda", 
            "admin@example.com", "900000001", "admin", store_id
        )
        
        # Vendedor
        vendor_id = await create_user(
            city_id, role_ids["Vendedor"], "30000000", "Vendedor", "Ejemplo", 
            "vendedor@example.com", "900000002", "vendedor", store_id
        )
        
        # Cliente
        customer_id = await create_user(
            city_id, role_ids["Cliente"], "40000000", "Cliente", "Ejemplo", 
            "cliente@example.com", "900000003", "cliente"
        )
        
        # Device
        device_user_id = await create_user(
            city_id, role_ids["Device"], "50000000", "Device", "Terminal", 
            "device@example.com", "900000004", "device", store_id
        )
        
        print("\n--- Siembra de datos completada ---")
        await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(seed())
