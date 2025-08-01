#!/usr/bin/env python3
"""
Script para probar la creación de un usuario después de la corrección de zona horaria.
Este script hace una petición HTTP directa al endpoint de creación de usuarios.
"""
import json
import requests
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_user_creation():
    """Prueba la creación de un usuario haciendo una petición HTTP al endpoint"""
    
    # URL del endpoint de creación de usuarios
    url = "http://localhost:8002/api/v1/users/"
    
    # Datos de prueba para el usuario
    # Generamos un DNI y username únicos basados en la hora actual
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    short_timestamp = datetime.now().strftime("%H%M%S")
    
    user_data = {
        "first_name": "Usuario",
        "middle_name": "",
        "last_name": "Prueba",
        "second_last_name": "",
        "email": f"test{timestamp}@example.com",
        "username": f"test{timestamp}",
        "dni": f"TEST{short_timestamp}",
        "prefix": "+57",
        "phone": "3209028935",
        "address": "Dirección de prueba",
        "city_id": "c3acd3c6-1b2d-467f-abbd-a367ce6bf34f",  # Asegúrate de usar un ID válido
        "role_id": "b57d8c89-5009-47f3-ac1f-b69b6f0887a3",  # Asegúrate de usar un ID válido
        "state": "Initial",
        "password": "password123"
    }
    
    logger.info(f"Intentando crear usuario: {user_data['username']}")
    
    try:
        # Hacer la petición POST
        response = requests.post(url, json=user_data)
        
        # Verificar la respuesta
        if response.status_code == 201:
            logger.info("¡Usuario creado exitosamente!")
            logger.info(f"Respuesta: {response.json()}")
            return True
        else:
            logger.error(f"Error al crear usuario. Código: {response.status_code}")
            logger.error(f"Respuesta: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Excepción al crear usuario: {e}")
        return False

if __name__ == "__main__":
    logger.info("Iniciando prueba de creación de usuario...")
    result = test_user_creation()
    
    if result:
        logger.info("La prueba fue exitosa. La corrección de zona horaria funcionó.")
    else:
        logger.error("La prueba falló. Es posible que se necesiten más correcciones.")
    
    logger.info("Prueba completada.")
