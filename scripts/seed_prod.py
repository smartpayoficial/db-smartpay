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
            client, "post", "/countries/", json={"name": "Peru", "code": "PE"}
        )
        if not country:
            print("No se pudo sembrar el país, abortando.")
            return
        country_id = country["country_id"]

        print("Seeding region…")
        region = await _request(
            client, "post", "/regions/", json={"name": "Lima", "country_id": country_id}
        )
        if not region:
            print("No se pudo sembrar la región, abortando.")
            return
        region_id = region["region_id"]

        print("Seeding city…")
        city = await _request(
            client,
            "post",
            "/cities/",
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
            "/roles/",
            json={
                "name": "Superadmin",
                "description": "Administrador de sistema principal",
            },
        )
        role_admin = await _request(
            client,
            "post",
            "/roles/",
            json={"name": "Admin", "description": "Administrador de plataforma"},
        )
        role_vendor = await _request(
            client,
            "post",
            "/roles/",
            json={"name": "Vendedor", "description": "Usuario vendedor"},
        )
        role_customer = await _request(
            client,
            "post",
            "/roles/",
            json={"name": "Cliente", "description": "Usuario final o cliente"},
        )
        role_device = await _request(
            client,
            "post",
            "/roles/",
            json={"name": "Device", "description": "Rol para el dispositivo"},
        )

        role_superadmin_id = role_superadmin["role_id"] if role_superadmin else None
        role_admin_id = role_admin["role_id"] if role_admin else None
        role_vendor_id = role_vendor["role_id"] if role_vendor else None
        role_customer_id = role_customer["role_id"] if role_customer else None
        role_device_id = role_device["role_id"] if role_device else None

        if not all(
            [
                role_superadmin_id,
                role_admin_id,
                role_vendor_id,
                role_customer_id,
                role_device_id,
            ]
        ):
            print("No se pudieron sembrar todos los roles, abortando.")
            return

        # --- Usuarios ---
        print("\nSeeding users…")

        # Usuario Superadmin
        user_superadmin = await _request(
            client,
            "post",
            "/users/",
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

        user_device = await _request(
            client,
            "post",
            "/users/",
            json={
                "city_id": city_id,
                "dni": "50000000",
                "first_name": "Device",
                "last_name": "Admin",
                "email": "deviceadmin@example.com",
                "prefix": "+51",
                "phone": "900000000",
                "address": "Calle Central 1",
                "username": "device",
                "password": "o5aX7R86Miq6",  # ¡En producción usa contraseñas fuertes y gestiona de forma segura!
                "role_id": role_device_id,
                "state": "Active",
            },
        )

        if not all([user_superadmin, user_device]):
            print(
                "No se pudieron sembrar todos los usuarios, abortando sim/device seed."
            )
            return

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
        await _request(
            client,
            "post",
            "/configurations",
            json={
                "key": "blocked_message",
                "value": "Tu dispositivo ha sido bloqueado por falta de pago. Regulariza tu deuda con tu operador para restablecer el acceso y uso del equipo.",
                "description": "Mensaje de bloqueo por pago",
            },
        )
        await _request(
            client,
            "post",
            "/configurations",
            json={
                "key": "blocked_sim",
                "value": "Tu dispositivo está bloqueado por una SIM no permitida. Inserta una SIM válida o contacta a tu operador para más información y desbloqueo.",
                "description": "Mensaje de bloqueo de SIM",
            },
        )
        await _request(
            client,
            "post",
            "/configurations",
            json={
                "key": "payment_message",
                "value": "Gracias por el pago.\nLa aplicación SmartPay te solicitará la desinstalación.",
                "description": "Mensaje de pago",
            },
        )

        print("\n✔ Base de datos poblada exitosamente.")


if __name__ == "__main__":
    asyncio.run(seed())
