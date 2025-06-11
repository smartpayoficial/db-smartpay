"""
Script para poblar la base de datos con datos de prueba para la tabla SIM.
Este script utiliza la API REST para crear, listar, actualizar y eliminar SIMs.
"""

import asyncio
from typing import Any, Dict, List, Optional

import httpx

# Configuración de la API
BASE_URL = "http://localhost:8002"  # Ajusta según tu configuración
API_PREFIX = "/api/v1"
SIM_ENDPOINT = f"{BASE_URL}{API_PREFIX}/sims"

# Datos de prueba
TEST_SIMS = [
    {
        "device_id": "00000000-0000-0000-0000-000000000001",  # Asegúrate de que este device exista
        "icc_id": "89314404000165000001",
        "slot_index": "0",
        "operator": "Movistar",
        "number": "+51987654321",
        "state": "Active",
    },
    {
        "device_id": "00000000-0000-0000-0000-000000000001",
        "icc_id": "89314404000165000002",
        "slot_index": "1",
        "operator": "Claro",
        "number": "+51987654322",
        "state": "Active",
    },
    {
        "device_id": "00000000-0000-0000-0000-000000000002",  # Asegúrate de que este device exista
        "icc_id": "89314404000165000003",
        "slot_index": "0",
        "operator": "Entel",
        "number": "+51987654323",
        "state": "Inactive",
    },
]


async def create_sim(sim_data: Dict[str, Any]) -> Dict[str, Any]:
    """Crea una nueva SIM a través de la API."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{SIM_ENDPOINT}", json=sim_data, timeout=10.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Error al crear SIM {sim_data.get('number')}: {e.response.text}")
            return {"error": str(e), "details": e.response.text}
        except Exception as e:
            print(f"Error inesperado al crear SIM {sim_data.get('number')}: {str(e)}")
            return {"error": str(e)}


async def get_sim(sim_id: str) -> Optional[Dict[str, Any]]:
    """Obtiene los detalles de una SIM por su ID."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{SIM_ENDPOINT}/{sim_id}", timeout=10.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                print(f"SIM con ID {sim_id} no encontrada")
            else:
                print(f"Error al obtener SIM {sim_id}: {e.response.text}")
            return None
        except Exception as e:
            print(f"Error inesperado al obtener SIM {sim_id}: {str(e)}")
            return None


async def update_sim(
    sim_id: str, update_data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """Actualiza una SIM existente."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.patch(
                f"{SIM_ENDPOINT}/{sim_id}", json=update_data, timeout=10.0
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Error al actualizar SIM {sim_id}: {e.response.text}")
            return None
        except Exception as e:
            print(f"Error inesperado al actualizar SIM {sim_id}: {str(e)}")
            return None


async def delete_sim(sim_id: str) -> bool:
    """Elimina una SIM."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(f"{SIM_ENDPOINT}/{sim_id}", timeout=10.0)
            response.raise_for_status()
            return True
        except httpx.HTTPStatusError as e:
            print(f"Error al eliminar SIM {sim_id}: {e.response.text}")
            return False
        except Exception as e:
            print(f"Error inesperado al eliminar SIM {sim_id}: {str(e)}")
            return False


async def list_all_sims() -> List[Dict[str, Any]]:
    """Lista todas las SIMs."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{SIM_ENDPOINT}", timeout=10.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Error al listar SIMs: {e.response.text}")
            return []
        except Exception as e:
            print(f"Error inesperado al listar SIMs: {str(e)}")
            return []


async def main():
    print("=== Iniciando población de datos de prueba para SIMs ===")

    # 1. Listar SIMs existentes
    print("\n--- SIMs existentes ---")
    existing_sims = await list_all_sims()
    print(f"Se encontraron {len(existing_sims)} SIMs existentes")

    # 2. Crear nuevas SIMs de prueba
    print("\n--- Creando SIMs de prueba ---")
    created_sims = []
    for sim_data in TEST_SIMS:
        print(f"Creando SIM con número: {sim_data['number']}")
        result = await create_sim(sim_data)
        if "error" not in result:
            created_sims.append(result)
            print(f"  → Creada con ID: {result.get('sim_id')}")
        else:
            print(f"  → Error: {result.get('details', 'Error desconocido')}")

    # 3. Listar todas las SIMs después de la creación
    print("\n--- Todas las SIMs después de la creación ---")
    all_sims = await list_all_sims()
    for sim in all_sims:
        print(
            f"ID: {sim.get('sim_id')} | Número: {sim.get('number')} | Operador: {sim.get('operator')} | Estado: {sim.get('state')}"
        )

    # 4. Actualizar una SIM de ejemplo (si se creó al menos una)
    if created_sims:
        sim_to_update = created_sims[0]
        print(f"\n--- Actualizando SIM {sim_to_update.get('number')} ---")
        update_result = await update_sim(
            sim_id=sim_to_update["sim_id"],
            update_data={"state": "Inactive", "operator": "Bitel"},
        )
        if update_result:
            print(f"SIM actualizada: {update_result}")

        # 5. Mostrar la SIM actualizada
        updated_sim = await get_sim(sim_to_update["sim_id"])
        if updated_sim:
            print(f"Detalles actualizados: {updated_sim}")

    print("\n=== Población de datos completada ===")


if __name__ == "__main__":
    asyncio.run(main())
