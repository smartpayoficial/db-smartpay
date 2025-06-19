"""Seed all core entities with at least one record each.

Run this from host with:

    python -m venv .venv && source .venv/bin/activate && pip install httpx && python scripts/seed_all.py

or from inside API container:

    docker exec -it docker-smartpay-db-api-1 python scripts/seed_all.py
"""

import asyncio
from typing import Any, Dict, Optional

import httpx


BASE_URL = "http://localhost:8002"
API_PREFIX = "/api/v1"


# Helper ----------------------------------------------------------------------------------
async def _request(
    client: httpx.AsyncClient, method: str, endpoint: str, **kwargs
) -> Optional[Dict[str, Any]]:
    """Helper function to make API requests and handle responses."""
    url = f"{BASE_URL}{API_PREFIX}{endpoint}"
    try:
        response = await client.request(method, url, timeout=10.0, **kwargs)

        if response.status_code in {200, 201}:
            print(f"    -> {method.upper()} {endpoint} {response.status_code} OK")
            return response.json()

        if response.status_code in {400, 409} and method.lower() == "post":
            list_resp = await client.get(
                f"{BASE_URL}{API_PREFIX}{endpoint}", timeout=10.0
            )
            if list_resp.status_code == 200 and list_resp.json():
                print(
                    f"    -> {method.upper()} {endpoint} {response.status_code}: Already exists. Using first record."
                )
                return list_resp.json()[0]

        print(
            f"    -> {method.upper()} {endpoint} {response.status_code}: {response.text}"
        )
    except httpx.RequestError as exc:
        print(f"    !! Error de red en {method.upper()} {url}: {exc}")
    except Exception as exc:
        print(f"    !! Error inesperado en {method.upper()} {url}: {exc}")
    return None


async def seed():
    async with httpx.AsyncClient() as client:
        print("\n--- Iniciando siembra de datos ---")

        # --- Geografía ---
        print("\nSeeding country…")
        country = await _request(
            client, "post", "/countries", json={"name": "Peru", "code": "PE"}
        )
        if not country:
            print("No se pudo sembrar el país, abortando.")
            return
        country_id = country["country_id"]

        print("Seeding region…")
        region = await _request(
            client, "post", "/regions", json={"name": "Lima", "country_id": country_id}
        )
        if not region:
            print("No se pudo sembrar la región, abortando.")
            return
        region_id = region["region_id"]

        print("Seeding city…")
        city = await _request(
            client,
            "post",
            "/cities",
            json={"name": "Lima", "region_id": region_id, "state": "Active"},
        )
        if not city:
            print("No se pudo sembrar la ciudad, abortando.")
            return
        city_id = city["city_id"]

        # --- Roles ---
        print("\nSeeding roles…")
        role_superadmin = await _request(
            client,
            "post",
            "/roles",
            json={
                "name": "Superadmin",
                "description": "Administrador de sistema principal",
            },
        )
        role_admin = await _request(
            client,
            "post",
            "/roles",
            json={"name": "Admin", "description": "Administrador de plataforma"},
        )
        role_vendor = await _request(
            client,
            "post",
            "/roles",
            json={"name": "Vendedor", "description": "Usuario vendedor"},
        )
        role_customer = await _request(
            client,
            "post",
            "/roles",
            json={"name": "Cliente", "description": "Usuario final o cliente"},
        )

        role_superadmin_id = role_superadmin["role_id"] if role_superadmin else None
        role_admin_id = role_admin["role_id"] if role_admin else None
        role_vendor_id = role_vendor["role_id"] if role_vendor else None
        role_customer_id = role_customer["role_id"] if role_customer else None

        if not all(
            [role_superadmin_id, role_admin_id, role_vendor_id, role_customer_id]
        ):
            print("No se pudieron sembrar todos los roles, abortando.")
            return

        # --- Usuarios ---
        print("\nSeeding users…")

        # Usuario Superadmin
        user_superadmin = await _request(
            client,
            "post",
            "/users",
            json={
                "city_id": city_id,
                "dni": "10000000",
                "first_name": "Admin",
                "last_name": "Maestro",
                "email": "superadmin@example.com",
                "prefix": "+51",
                "phone": "900000000",
                "address": "Calle Central 1",
                "username": "superadmin",
                "password": "secret",  # ¡En producción usa contraseñas fuertes y gestiona de forma segura!
                "role_id": role_superadmin_id,
                "state": "Active",
            },
        )

        # Usuario Admin
        user_admin = await _request(
            client,
            "post",
            "/users",
            json={
                "city_id": city_id,
                "dni": "20000000",
                "first_name": "Admin",
                "last_name": "General",
                "email": "admin@example.com",
                "prefix": "+51",
                "phone": "911111111",
                "address": "Avenida Admin 2",
                "username": "admin",
                "password": "secret",
                "role_id": role_admin_id,
                "state": "Active",
            },
        )

        # Usuario Vendedor
        user_vendor_obj = await _request(
            client,
            "post",
            "/users",
            json={
                "city_id": city_id,
                "dni": "30000000",
                "first_name": "Vendedor",
                "last_name": "Uno",
                "email": "vendedor@example.com",
                "prefix": "+51",
                "phone": "922222222",
                "address": "Pasaje Comercio 3",
                "username": "vendedor",
                "password": "secret",
                "role_id": role_vendor_id,
                # Only 'Active' or 'Inactive' are allowed for state
                "state": "Active",
            },
        )
        vendor_id = user_vendor_obj["user_id"] if user_vendor_obj else None

        # Usuario Cliente
        user_customer_obj = await _request(
            client,
            "post",
            "/users",
            json={
                "city_id": city_id,
                "dni": "40000000",
                "first_name": "Cliente",
                "last_name": "Feliz",
                "email": "cliente@example.com",
                "prefix": "+51",
                "phone": "933333333",
                "address": "Urbanización Residencial 4",
                "username": "cliente",
                "password": "secret",
                "role_id": role_customer_id,
                "state": "Active",
            },
        )
        customer_id = user_customer_obj["user_id"] if user_customer_obj else None

        if not all([user_superadmin, user_admin, user_vendor_obj, user_customer_obj]):
            print(
                "No se pudieron sembrar todos los usuarios, abortando sim/device seed."
            )
            return

        # --- Enrolment, Device, SIM (usando el vendedor y un cliente) ---
        print("\nSeeding enrolment…")
        enrolment = await _request(
            client,
            "post",
            "/enrolments",
            json={"user_id": customer_id, "vendor_id": vendor_id},
        )
        print("enrolment response:", enrolment)
        if not enrolment or "enrolment_id" not in enrolment:
            print("Error: enrolment no creado correctamente o falta enrolment_id")
            return
        if not enrolment:
            print("No se pudo sembrar el enrolamiento, abortando device/sim seed.")
            return
        enrolment_id = enrolment["enrolment_id"]

        print("Seeding device…")
        device_payload = {
            "enrolment_id": enrolment_id,
            "name": "Dispositivo Prueba",
            "imei": "358240051111110",
            "imei_two": "358240051111111",
            "serial_number": "SN123456",
            "model": "Model X",
            "brand": "BrandY",
            "product_name": "ProductZ",
            # Only 'Active' or 'Inactive' are allowed for state
            "state": "Active",  # Changed to 'Active'
            "serial_number": "SNTEST123",
            "model": "ModeloXYZ",
            "brand": "MarcaABC",
            "product_name": "ProductoDEF",
            "state": "Active",
        }
        print("device payload:", device_payload)
        device = await _request(client, "post", "/devices", json=device_payload)
        print("device response:", device)
        if not device or not isinstance(device, dict) or "device_id" not in device:
            print(
                "Error: device no creado correctamente o falta device_id. Respuesta:",
                device,
            )
            return
        if not device:
            print("No se pudo sembrar el dispositivo, abortando sim seed.")
            return
        device_id = device["device_id"]

        print("Seeding sim…")
        await _request(
            client,
            "post",
            "/sims",
            json={
                "device_id": device_id,
                "icc_id": "89314404000165000001",
                "slot_index": "0",
                "operator": "Claro",
                "number": "+51987654321",
                # Only 'Active' or 'Inactive' are allowed for state
                "state": "Active",  # Changed to 'Active'
            },
        )

        # --- Payment (usando el device creado y un plan ficticio) ---

        plan_id = None
        plans = await _request(client, "get", "/plans")
        if plans and isinstance(plans, list) and len(plans) > 0:
            plan_id = plans[0]["plan_id"]
        else:
            # Crea un plan dummy si no existe
            plan_payload = {
                "user_id": customer_id,
                "vendor_id": vendor_id,
                "device_id": device_id,
                "initial_date": "2025-01-01",
                "quotas": 12,
                "contract": "Contrato demo"
            }
            plan = await _request(client, "post", "/plans", json=plan_payload)
            plan_id = plan["plan_id"] if plan else None
        if plan_id:
            payment_payload = {
                "device_id": device_id,
                "plan_id": plan_id,
                "value": "100.00",
                "method": "card",
                "state": "Approved",
                "date": "2025-01-01T12:00:00",
                "reference": "PAYMENTREF001"
            }
            payment = await _request(client, "post", "/payments", json=payment_payload)
            print("payment response:", payment)
        else:
            print("No se pudo crear un plan para asociar al pago, omitiendo payment seed.")

        # --- Configuración ---
        print("\nSeeding configuration…")
        await _request(
            client,
            "post",
            "/configurations",
            json={"key": "site_name", "value": "SmartPay", "description": "Site name"},
        )
        await _request(
            client,
            "post",
            "/configurations",
            json={
                "key": "admin_email",
                "value": "contacto@smartpay.com",
                "description": "Email de contacto del administrador",
            },
        )

        print("\n✔ Base de datos poblada exitosamente.")


if __name__ == "__main__":
    asyncio.run(seed())
