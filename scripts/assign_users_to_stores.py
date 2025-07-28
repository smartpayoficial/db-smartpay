#!/usr/bin/env python
"""
Script para asignar usuarios a tiendas de forma masiva.
Este script puede ser utilizado después de la migración que agrega store_id a la tabla user.
"""
import asyncio
import argparse
import csv
import os
import sys
from uuid import UUID

# Añadir el directorio raíz del proyecto al path de Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tortoise import Tortoise

# En lugar de usar settings, obtenemos la URL de la base de datos directamente
DATABASE_URL = os.environ.get('POSTGRES_DATABASE_URL', 'postgres://postgres:postgres@localhost:5436/smartpay')

from app.services.user import user_service
from app.services.store import store_service
from app.schemas.user import UserUpdate


async def init_db():
    """Inicializar conexión a la base de datos."""
    await Tortoise.init(
        db_url=DATABASE_URL,
        modules={"models": ["app.infra.postgres.models"]}
    )


async def close_db():
    """Cerrar conexión a la base de datos."""
    await Tortoise.close_connections()


async def assign_users_by_csv(csv_file):
    """
    Asignar usuarios a tiendas usando un archivo CSV.
    
    El formato del CSV debe ser:
    user_dni,store_id
    123456789,550e8400-e29b-41d4-a716-446655440000
    987654321,550e8400-e29b-41d4-a716-446655440001
    """
    print(f"Procesando archivo CSV: {csv_file}")
    
    # Contadores para estadísticas
    total = 0
    success = 0
    not_found = 0
    errors = 0
    
    try:
        with open(csv_file, 'r') as f:
            reader = csv.reader(f)
            # Saltar encabezado
            next(reader, None)
            
            for row in reader:
                total += 1
                if len(row) < 2:
                    print(f"Error: Fila {total} no tiene suficientes columnas")
                    errors += 1
                    continue
                
                user_dni, store_id = row[0], row[1]
                
                try:
                    # Validar UUID
                    store_uuid = UUID(store_id)
                    
                    # Verificar que la tienda existe
                    store = await store_service.get(id=store_uuid)
                    if not store:
                        print(f"Error: Tienda con ID {store_id} no encontrada")
                        not_found += 1
                        continue
                    
                    # Buscar usuario por DNI
                    user = await user_service.get_by_dni(dni=user_dni)
                    if not user:
                        print(f"Error: Usuario con DNI {user_dni} no encontrado")
                        not_found += 1
                        continue
                    
                    # Actualizar usuario con store_id
                    user_update = UserUpdate(store_id=store_uuid)
                    await user_service.update(id=user.user_id, obj_in=user_update)
                    
                    print(f"Usuario {user.first_name} {user.last_name} (DNI: {user_dni}) asignado a tienda {store.nombre}")
                    success += 1
                    
                except ValueError:
                    print(f"Error: ID de tienda inválido: {store_id}")
                    errors += 1
                except Exception as e:
                    print(f"Error al procesar usuario {user_dni}: {str(e)}")
                    errors += 1
    
    except FileNotFoundError:
        print(f"Error: Archivo {csv_file} no encontrado")
        return False
    except Exception as e:
        print(f"Error al procesar el archivo CSV: {str(e)}")
        return False
    
    # Mostrar estadísticas
    print("\nEstadísticas:")
    print(f"Total de registros procesados: {total}")
    print(f"Asignaciones exitosas: {success}")
    print(f"Registros no encontrados: {not_found}")
    print(f"Errores: {errors}")
    
    return success > 0


async def assign_all_users_to_store(store_id):
    """Asignar todos los usuarios a una tienda específica."""
    try:
        store_uuid = UUID(store_id)
        
        # Verificar que la tienda existe
        store = await store_service.get(id=store_uuid)
        if not store:
            print(f"Error: Tienda con ID {store_id} no encontrada")
            return False
        
        # Obtener todos los usuarios
        users = await user_service.get_all(skip=0, limit=1000)
        
        # Contadores para estadísticas
        total = len(users)
        success = 0
        errors = 0
        
        for user in users:
            try:
                # Actualizar usuario con store_id
                user_update = UserUpdate(store_id=store_uuid)
                await user_service.update(id=user.user_id, obj_in=user_update)
                
                print(f"Usuario {user.first_name} {user.last_name} asignado a tienda {store.nombre}")
                success += 1
                
            except Exception as e:
                print(f"Error al asignar usuario {user.user_id}: {str(e)}")
                errors += 1
        
        # Mostrar estadísticas
        print("\nEstadísticas:")
        print(f"Total de usuarios: {total}")
        print(f"Asignaciones exitosas: {success}")
        print(f"Errores: {errors}")
        
        return success > 0
        
    except ValueError:
        print(f"Error: ID de tienda inválido: {store_id}")
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False


async def list_users_without_store():
    """Listar usuarios que no tienen tienda asignada."""
    try:
        # Obtener usuarios sin tienda
        from tortoise.expressions import Q
        users = await user_service.get_all_with_filter(Q(store_id__isnull=True))
        
        if not users:
            print("No hay usuarios sin tienda asignada.")
            return True
        
        print(f"Usuarios sin tienda asignada ({len(users)}):")
        print("-" * 80)
        print(f"{'ID':36} | {'DNI':12} | {'Nombre':30} | {'Email':30}")
        print("-" * 80)
        
        for user in users:
            print(f"{str(user.user_id):36} | {user.dni:12} | {user.first_name} {user.last_name:25} | {user.email:30}")
        
        return True
        
    except Exception as e:
        print(f"Error al listar usuarios: {str(e)}")
        return False


async def main():
    parser = argparse.ArgumentParser(description="Herramienta para asignar usuarios a tiendas")
    
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")
    
    # Comando para asignar usuarios por CSV
    csv_parser = subparsers.add_parser("csv", help="Asignar usuarios a tiendas usando un archivo CSV")
    csv_parser.add_argument("file", help="Ruta al archivo CSV con formato: user_dni,store_id")
    
    # Comando para asignar todos los usuarios a una tienda
    all_parser = subparsers.add_parser("all", help="Asignar todos los usuarios a una tienda específica")
    all_parser.add_argument("store_id", help="ID de la tienda a la que asignar todos los usuarios")
    
    # Comando para listar usuarios sin tienda
    subparsers.add_parser("list", help="Listar usuarios que no tienen tienda asignada")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Inicializar base de datos
    await init_db()
    
    try:
        if args.command == "csv":
            await assign_users_by_csv(args.file)
        elif args.command == "all":
            await assign_all_users_to_store(args.store_id)
        elif args.command == "list":
            await list_users_without_store()
    finally:
        # Cerrar conexión a la base de datos
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())
