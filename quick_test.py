#!/usr/bin/env python3
"""
Script rápido de pruebas para el servicio SmartPay
Uso: python quick_test.py [endpoint]
"""

import json
import sys

import requests

BASE_URL = "http://localhost:8002"
HEADERS = {"Content-Type": "application/json"}


def test_health():
    """Probar health check"""
    print("🔍 Testing health check...")
    response = requests.get(f"{BASE_URL}/health-check")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()


def test_get_all(endpoint):
    """Probar GET en cualquier endpoint"""
    print(f"🔍 Testing GET /{endpoint}/...")
    response = requests.get(f"{BASE_URL}/{endpoint}/")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Items found: {len(data) if isinstance(data, list) else 'N/A'}")
        if isinstance(data, list) and len(data) > 0:
            print(f"First item: {json.dumps(data[0], indent=2)}")
    else:
        print(f"Error: {response.text}")
    print()


def test_sample_user(city_id=None):
    """Crear usuario de muestra"""
    if not city_id:
        print("❌ Necesita city_id para crear usuario")
        return

    user_data = {
        "city_id": city_id,
        "dni": "99999999",
        "first_name": "Quick",
        "last_name": "Test",
        "email": "quick@test.com",
        "prefix": "+1",
        "phone": "5555555555",
        "address": "Quick Test St 123",
    }

    print("🔍 Testing user creation...")
    response = requests.post(f"{BASE_URL}/users/", json=user_data, headers=HEADERS)
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        print("✅ Usuario creado correctamente")
        print(f"User ID: {response.json()['user_id']}")
    else:
        print(f"❌ Error: {response.text}")
    print()


def main():
    if len(sys.argv) > 1:
        endpoint = sys.argv[1]
        if endpoint == "health":
            test_health()
        else:
            test_get_all(endpoint)
    else:
        print("🧪 QUICK TEST - SmartPay Service")
        print("=" * 40)

        # Test básicos
        test_health()
        test_get_all("countries")
        test_get_all("regions")
        test_get_all("cities")
        test_get_all("users")
        test_get_all("enrolments")
        test_get_all("devices")

        print("📖 Uso:")
        print("  python quick_test.py health      # Solo health check")
        print("  python quick_test.py users       # Solo usuarios")
        print("  python quick_test.py devices     # Solo dispositivos")


if __name__ == "__main__":
    main()
