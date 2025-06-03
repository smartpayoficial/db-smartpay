#!/usr/bin/env python3
"""
Script de pruebas para el servicio SmartPay
Verifica funcionalidad básica y validaciones únicas implementadas
"""

import random
import time

import requests

# Configuración
BASE_URL = "http://localhost:8002"
HEADERS = {"Content-Type": "application/json"}

# Generar datos únicos con timestamp
timestamp = int(time.time())
random_suffix = random.randint(1000, 9999)


# Colores para output
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    END = "\033[0m"
    BOLD = "\033[1m"


def log_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")


def log_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.END}")


def log_info(message):
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")


def log_warning(message):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")


def test_health_check():
    """Verificar que el servicio está corriendo"""
    log_info("Probando health check...")
    try:
        response = requests.get(f"{BASE_URL}/health-check")
        if response.status_code == 200:
            log_success("Servicio funcionando correctamente")
            return True
        else:
            log_error(f"Health check falló: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        log_error("No se pudo conectar al servicio. ¿Está corriendo en localhost:8002?")
        return False


def create_test_data():
    """Crear datos de prueba necesarios"""
    log_info("Creando datos de prueba...")

    test_data = {}

    # 1. Crear país
    country_data = {
        "name": f"Test Country {timestamp}",
        "code": f"T{random_suffix%99:02d}",  # Código de 3 caracteres único
    }
    response = requests.post(
        f"{BASE_URL}/countries/", json=country_data, headers=HEADERS
    )
    if response.status_code == 201:
        test_data["country_id"] = response.json()["country_id"]
        log_success("País de prueba creado")
    else:
        log_error(f"Error creando país: {response.status_code} - {response.text}")
        return None

    # 2. Crear región
    region_data = {
        "name": f"Test Region {timestamp}",
        "country_id": test_data["country_id"],
    }
    response = requests.post(f"{BASE_URL}/regions/", json=region_data, headers=HEADERS)
    if response.status_code == 201:
        test_data["region_id"] = response.json()["region_id"]
        log_success("Región de prueba creada")
    else:
        log_error(f"Error creando región: {response.status_code} - {response.text}")
        return None

    # 3. Crear ciudad
    city_data = {"name": f"Test City {timestamp}", "region_id": test_data["region_id"]}
    response = requests.post(f"{BASE_URL}/cities/", json=city_data, headers=HEADERS)
    if response.status_code == 201:
        test_data["city_id"] = response.json()["city_id"]
        log_success("Ciudad de prueba creada")
    else:
        log_error(f"Error creando ciudad: {response.status_code} - {response.text}")
        return None

    return test_data


def test_user_prefix_validation(city_id):
    """Probar validación de prefix en usuarios"""
    log_info("Probando validación de prefix en usuarios...")

    # Caso 1: Prefix válido (<=4 caracteres)
    user_data = {
        "city_id": city_id,
        "dni": f"{timestamp%100000000:08d}",  # DNI único basado en timestamp
        "first_name": "Test",
        "last_name": "User",
        "email": f"test{timestamp}@example.com",  # Email único
        "prefix": "+57",  # 3 caracteres - válido
        "phone": f"{random_suffix}567890",
        "address": f"Test Address {timestamp}",
    }

    response = requests.post(f"{BASE_URL}/users/", json=user_data, headers=HEADERS)
    if response.status_code == 201:
        log_success("Usuario con prefix válido creado correctamente")
        user_id = response.json()["user_id"]
    else:
        log_error(
            f"Error creando usuario con prefix válido: {response.status_code} - {response.text}"
        )
        return None

    # Caso 2: Prefix inválido (>4 caracteres)
    user_data_invalid = user_data.copy()
    user_data_invalid["dni"] = f"{(timestamp+1)%100000000:08d}"  # DNI diferente
    user_data_invalid["email"] = f"test{timestamp+1}@example.com"  # Email diferente
    user_data_invalid["prefix"] = "+5712"  # 5 caracteres - inválido

    response = requests.post(
        f"{BASE_URL}/users/", json=user_data_invalid, headers=HEADERS
    )
    if response.status_code == 422:  # Validation error
        log_success("Validación de prefix funcionando - rechazó prefix > 4 caracteres")
    else:
        log_warning(
            f"Debería rechazar prefix > 4 caracteres. Status: {response.status_code}"
        )

    return user_id


def test_enrolment_and_device_uniqueness(user_id):
    """Probar unicidad de enrolment_id y IMEIs"""
    log_info("Probando unicidad de enrolment_id y IMEIs...")

    # 1. Crear enrollamiento
    enrolment_data = {
        "user_id": user_id,
        "vendor_id": user_id,  # Usando mismo usuario como vendor para simplificar
    }

    response = requests.post(
        f"{BASE_URL}/enrolments/", json=enrolment_data, headers=HEADERS
    )
    if response.status_code == 201:
        enrolment_id = response.json()["enrolment_id"]
        log_success("Enrollamiento creado correctamente")
    else:
        log_error(
            f"Error creando enrollamiento: {response.status_code} - {response.text}"
        )
        return

    # 2. Crear primer dispositivo
    device_data = {
        "enrolment_id": enrolment_id,
        "name": f"Test Device {timestamp}",
        "imei": f"{timestamp%999999999999999:015d}",  # IMEI único
        "imei_two": f"{(timestamp+1)%999999999999999:015d}",  # IMEI_TWO único
        "serial_number": f"SN{timestamp}",
        "model": "Test Model",
        "brand": "Test Brand",
        "product_name": "Test Product",
    }

    response = requests.post(f"{BASE_URL}/devices/", json=device_data, headers=HEADERS)
    if response.status_code == 201:
        log_success("Primer dispositivo creado correctamente")
    else:
        log_error(
            f"Error creando primer dispositivo: {response.status_code} - {response.text}"
        )
        return

    # 3. Intentar crear segundo dispositivo con mismo enrolment_id (debería fallar)
    log_info("Probando duplicación de enrolment_id...")
    device_data_dup_enrolment = device_data.copy()
    device_data_dup_enrolment["name"] = f"Test Device {timestamp+1}"
    device_data_dup_enrolment["imei"] = f"{(timestamp+10)%999999999999999:015d}"
    device_data_dup_enrolment["imei_two"] = f"{(timestamp+11)%999999999999999:015d}"
    device_data_dup_enrolment["serial_number"] = f"SN{timestamp+1}"

    response = requests.post(
        f"{BASE_URL}/devices/", json=device_data_dup_enrolment, headers=HEADERS
    )
    if response.status_code == 400:
        log_success("✅ Correctamente rechazó enrolment_id duplicado")
    else:
        log_error(
            f"❌ Debería rechazar enrolment_id duplicado. Status: {response.status_code}"
        )

    # 4. Crear segundo enrollamiento para probar IMEIs únicos
    enrolment_data2 = {"user_id": user_id, "vendor_id": user_id}

    response = requests.post(
        f"{BASE_URL}/enrolments/", json=enrolment_data2, headers=HEADERS
    )
    if response.status_code == 201:
        enrolment_id2 = response.json()["enrolment_id"]
    else:
        log_error(f"Error creando segundo enrollamiento: {response.status_code}")
        return

    # 5. Intentar crear dispositivo con IMEI duplicado
    log_info("Probando duplicación de IMEI...")
    device_data_dup_imei = {
        "enrolment_id": enrolment_id2,
        "name": f"Test Device {timestamp+2}",
        "imei": device_data["imei"],  # IMEI duplicado del primer dispositivo
        "imei_two": f"{(timestamp+20)%999999999999999:015d}",
        "serial_number": f"SN{timestamp+2}",
        "model": "Test Model",
        "brand": "Test Brand",
        "product_name": "Test Product",
    }

    response = requests.post(
        f"{BASE_URL}/devices/", json=device_data_dup_imei, headers=HEADERS
    )
    if response.status_code == 400:
        log_success("✅ Correctamente rechazó IMEI duplicado")
    else:
        log_error(f"❌ Debería rechazar IMEI duplicado. Status: {response.status_code}")

    # 6. Intentar crear dispositivo con IMEI_TWO duplicado
    log_info("Probando duplicación de IMEI_TWO...")
    device_data_dup_imei2 = {
        "enrolment_id": enrolment_id2,
        "name": f"Test Device {timestamp+3}",
        "imei": f"{(timestamp+30)%999999999999999:015d}",
        "imei_two": device_data[
            "imei_two"
        ],  # IMEI_TWO duplicado del primer dispositivo
        "serial_number": f"SN{timestamp+3}",
        "model": "Test Model",
        "brand": "Test Brand",
        "product_name": "Test Product",
    }

    response = requests.post(
        f"{BASE_URL}/devices/", json=device_data_dup_imei2, headers=HEADERS
    )
    if response.status_code == 400:
        log_success("✅ Correctamente rechazó IMEI_TWO duplicado")
    else:
        log_error(
            f"❌ Debería rechazar IMEI_TWO duplicado. Status: {response.status_code}"
        )


def main():
    """Función principal de pruebas"""
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("=" * 60)
    print("🧪 SCRIPT DE PRUEBAS - SMARTPAY SERVICE")
    print(f"🕐 Timestamp: {timestamp} | Random: {random_suffix}")
    print("=" * 60)
    print(f"{Colors.END}")

    # 1. Verificar que el servicio está corriendo
    if not test_health_check():
        return

    # 2. Crear datos de prueba
    test_data = create_test_data()
    if not test_data:
        log_error("No se pudieron crear los datos de prueba")
        return

    # 3. Probar validación de prefix
    user_id = test_user_prefix_validation(test_data["city_id"])
    if not user_id:
        log_error("No se pudo crear usuario de prueba")
        return

    # 4. Probar unicidad de enrolment_id y IMEIs
    test_enrolment_and_device_uniqueness(user_id)

    print(f"\n{Colors.BOLD}{Colors.GREEN}")
    print("=" * 60)
    print("🎉 PRUEBAS COMPLETADAS")
    print("=" * 60)
    print(f"{Colors.END}")

    log_info("Para limpiar datos de prueba, puedes recrear la base de datos con:")
    log_info("sudo ./recreate_database.sh")


if __name__ == "__main__":
    main()
