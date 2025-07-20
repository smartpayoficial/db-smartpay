#!/usr/bin/env python3
import os
import subprocess
import sys

def run_command(command):
    """Ejecuta un comando y muestra la salida en tiempo real"""
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    
    for line in process.stdout:
        print(line, end='')
    
    process.wait()
    return process.returncode

def main():
    # Ruta al script SQL
    sql_script = "db/insert_countries_regions_cities.sql"
    
    # Verificar que el script existe
    if not os.path.exists(sql_script):
        print(f"Error: El archivo {sql_script} no existe.")
        sys.exit(1)
    
    print("=== Insertando países, regiones y ciudades en la base de datos ===")
    
    # Paso 1: Asegurarse de que la extensión UUID esté habilitada
    print("\n1. Habilitando extensión UUID...")
    uuid_command = 'docker exec -i docker-smartpay-db-v12-1 psql -U postgres -d smartpay -c "CREATE EXTENSION IF NOT EXISTS \\"uuid-ossp\\";";'
    if run_command(uuid_command) != 0:
        print("Error al habilitar la extensión UUID.")
        sys.exit(1)
    
    # Paso 2: Ejecutar el script SQL
    print("\n2. Ejecutando script SQL para insertar datos...")
    sql_command = f'docker exec -i docker-smartpay-db-v12-1 psql -U postgres -d smartpay < {sql_script}'
    if run_command(sql_command) != 0:
        print("Error al ejecutar el script SQL.")
        sys.exit(1)
    
    # Paso 3: Verificar que los datos se insertaron correctamente
    print("\n3. Verificando la inserción de datos...")
    verify_command = 'docker exec -i docker-smartpay-db-v12-1 psql -U postgres -d smartpay -c "SELECT COUNT(*) FROM country; SELECT COUNT(*) FROM region; SELECT COUNT(*) FROM city;"'
    if run_command(verify_command) != 0:
        print("Error al verificar los datos.")
        sys.exit(1)
    
    print("\n=== Proceso completado con éxito ===")
    print("Los países, regiones y ciudades han sido insertados en la base de datos.")

if __name__ == "__main__":
    main()
