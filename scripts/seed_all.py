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
    url = f"{BASE_URL}{API_PREFIX}{endpoint}"
    try:
        response = await client.request(method, url, timeout=10.0, **kwargs)
        if response.status_code in {200, 201}:
            return response.json()

        # Duplicate / already exists handling (400 or 409)
        if response.status_code in {400, 409} and method.lower() == "post":
            list_resp = await client.get(url, timeout=10.0)
            if list_resp.status_code == 200 and list_resp.json():
                return list_resp.json()[0]
        print(
            f"    -> {method.upper()} {endpoint} {response.status_code}: {response.text}"
        )
    except Exception as exc:
        print(f"    !! Error on {method.upper()} {endpoint}: {exc}")
    return None


async def seed():
    async with httpx.AsyncClient() as client:
        print("Seeding country…")
        country = await _request(
            client, "post", "/countries", json={"name": "Peru", "code": "PE"}
        )
        if not country:
            return
        country_id = country["country_id"]

        print("Seeding region…")
        region = await _request(
            client, "post", "/regions", json={"name": "Lima", "country_id": country_id}
        )
        region_id = region["region_id"]

        print("Seeding city…")
        city = await _request(
            client,
            "post",
            "/cities",
            json={"name": "Lima", "region_id": region_id, "state": "Active"},
        )
        city_id = city["city_id"]

        print("Seeding roles…")
        role_customer = await _request(
            client,
            "post",
            "/roles",
            json={"name": "Customer", "description": "End user"},
        )
        role_vendor = await _request(
            client,
            "post",
            "/roles",
            json={"name": "Vendor", "description": "Vendor user"},
        )
        role_customer_id = role_customer["role_id"]
        role_vendor_id = role_vendor["role_id"]

        print("Seeding users…")
        user_customer = await _request(
            client,
            "post",
            "/users",
            json={
                "city_id": city_id,
                "dni": "12345678",
                "first_name": "Juan",
                "middle_name": None,
                "last_name": "Perez",
                "second_last_name": None,
                "email": "juan@example.com",
                "prefix": "+51",
                "phone": "999888777",
                "address": "Calle Falsa 123",
                "username": "juan",
                "password": "secret",
                "role_id": role_customer_id,
                "state": "Active",
            },
        )
        user_vendor = await _request(
            client,
            "post",
            "/users",
            json={
                "city_id": city_id,
                "dni": "87654321",
                "first_name": "Vendedor",
                "middle_name": None,
                "last_name": "Uno",
                "second_last_name": None,
                "email": "vendor@example.com",
                "prefix": "+51",
                "phone": "912345678",
                "address": "Avenida Siempre Viva 742",
                "username": "vendor",
                "password": "secret",
                "role_id": role_vendor_id,
                "state": "Active",
            },
        )
        user_id = user_customer and user_customer.get("user_id")
        vendor_id = user_vendor and user_vendor.get("user_id")
        if not user_id or not vendor_id:
            print("No pude obtener usuarios: abortando sim/device seed")
            return

        print("Seeding enrolment…")
        enrolment = await _request(
            client,
            "post",
            "/enrolments",
            json={"user_id": user_id, "vendor_id": vendor_id},
        )
        enrolment_id = enrolment["enrolment_id"]

        print("Seeding device…")
        device_payload = {
            "enrolment_id": enrolment_id,
            "name": "Phone 1",
            "imei": "358240051111110",
            "imei_two": "358240051111111",
            "serial_number": "SN123456",
            "model": "Model X",
            "brand": "BrandY",
            "product_name": "ProductZ",
            "state": "Active",
        }
        device = await _request(client, "post", "/devices", json=device_payload)
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
                "operator": "Movistar",
                "number": "+51987654321",
                "state": "Active",
            },
        )

        print("Seeding configuration…")
        await _request(
            client,
            "post",
            "/configurations",
            json={"key": "site_name", "value": "SmartPay", "description": "Site name"},
        )

        print("✔ Base de datos poblada.")


if __name__ == "__main__":
    asyncio.run(seed())
