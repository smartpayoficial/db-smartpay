#!/usr/bin/env python3
import asyncio
import uuid
from typing import Dict, List

# Importamos las configuraciones y modelos necesarios
from app.core.config import settings
from app.core.database import init_db
from app.infra.postgres.models.country import Country
from app.infra.postgres.models.region import Region
from app.infra.postgres.models.city import City

# Datos de países
COUNTRIES = [
    {"name": "Argentina", "code": "AR"},
    {"name": "Bolivia", "code": "BO"},
    {"name": "Brazil", "code": "BR"},
    {"name": "Chile", "code": "CL"},
    {"name": "Colombia", "code": "CO"},
    {"name": "Costa Rica", "code": "CR"},
    {"name": "Cuba", "code": "CU"},
    {"name": "Dominican Republic", "code": "DO"},
    {"name": "Ecuador", "code": "EC"},
    {"name": "El Salvador", "code": "SV"},
    {"name": "Guatemala", "code": "GT"},
    {"name": "Honduras", "code": "HN"},
    {"name": "Mexico", "code": "MX"},
    {"name": "Nicaragua", "code": "NI"},
    {"name": "Panama", "code": "PA"},
    {"name": "Paraguay", "code": "PY"},
    {"name": "Peru", "code": "PE"},
    {"name": "Uruguay", "code": "UY"},
    {"name": "Venezuela", "code": "VE"}
]

# Datos de regiones y ciudades por país
REGIONS_AND_CITIES = {
    "Colombia": [
        {
            "name": "Bogotá D.C.",
            "cities": ["Bogotá"]
        },
        {
            "name": "Antioquia",
            "cities": ["Medellín", "Envigado", "Itagüí"]
        },
        {
            "name": "Valle del Cauca",
            "cities": ["Cali", "Palmira", "Buga"]
        },
        {
            "name": "Cundinamarca",
            "cities": ["Soacha", "Zipaquirá", "Chía"]
        },
        {
            "name": "Atlántico",
            "cities": []
        },
        {
            "name": "Santander",
            "cities": []
        },
        {
            "name": "Bolívar",
            "cities": []
        }
    ],
    "Mexico": [
        {
            "name": "Jalisco",
            "cities": ["Guadalajara", "Zapopan", "Tlaquepaque"]
        },
        {
            "name": "Ciudad de México",
            "cities": []
        },
        {
            "name": "Estado de México",
            "cities": ["Naucalpan de Juárez", "Ecatepec de Morelos", "Nezahualcóyotl"]
        },
        {
            "name": "Nuevo León",
            "cities": []
        },
        {
            "name": "Veracruz",
            "cities": []
        },
        {
            "name": "Puebla",
            "cities": []
        }
    ],
    "Argentina": [
        {
            "name": "Buenos Aires (Provincia)",
            "cities": ["La Plata", "Mar del Plata", "Bahía Blanca"]
        },
        {
            "name": "Ciudad Autónoma de Buenos Aires",
            "cities": []
        },
        {
            "name": "Córdoba",
            "cities": []
        },
        {
            "name": "Santa Fe",
            "cities": []
        }
    ],
    "Brazil": [
        {
            "name": "São Paulo",
            "cities": ["São Paulo", "Guarulhos", "Campinas"]
        },
        {
            "name": "Rio de Janeiro",
            "cities": ["Rio de Janeiro", "Niterói", "Duque de Caxias"]
        },
        {
            "name": "Minas Gerais",
            "cities": []
        },
        {
            "name": "Bahia",
            "cities": []
        }
    ],
    "Chile": [
        {
            "name": "Región Metropolitana de Santiago",
            "cities": ["Santiago", "Puente Alto"]
        },
        {
            "name": "Valparaíso",
            "cities": ["Valparaíso", "Viña del Mar"]
        }
    ],
    "Peru": [
        {
            "name": "Lima",
            "cities": ["Lima", "Callao"]
        },
        {
            "name": "Cusco",
            "cities": ["Cusco"]
        }
    ],
    "Ecuador": [
        {
            "name": "Pichincha",
            "cities": ["Quito"]
        },
        {
            "name": "Guayas",
            "cities": ["Guayaquil"]
        }
    ],
    "Bolivia": [
        {
            "name": "La Paz",
            "cities": ["La Paz", "El Alto"]
        },
        {
            "name": "Santa Cruz",
            "cities": ["Santa Cruz de la Sierra"]
        }
    ],
    "Uruguay": [
        {
            "name": "Montevideo",
            "cities": ["Montevideo"]
        }
    ],
    "Paraguay": [
        {
            "name": "Central",
            "cities": ["Asunción", "Luque"]
        }
    ],
    "Venezuela": [
        {
            "name": "Distrito Capital",
            "cities": ["Caracas"]
        },
        {
            "name": "Zulia",
            "cities": ["Maracaibo"]
        }
    ],
    "Costa Rica": [
        {
            "name": "San José",
            "cities": ["San José"]
        }
    ],
    "Panama": [
        {
            "name": "Panamá",
            "cities": ["Panamá City"]
        }
    ],
    "Guatemala": [
        {
            "name": "Guatemala",
            "cities": ["Guatemala City"]
        }
    ],
    "El Salvador": [
        {
            "name": "San Salvador",
            "cities": ["San Salvador"]
        }
    ],
    "Honduras": [
        {
            "name": "Francisco Morazán",
            "cities": ["Tegucigalpa"]
        }
    ],
    "Nicaragua": [
        {
            "name": "Managua",
            "cities": ["Managua"]
        }
    ],
    "Cuba": [
        {
            "name": "La Habana",
            "cities": ["Havana"]
        }
    ],
    "Dominican Republic": [
        {
            "name": "Distrito Nacional",
            "cities": ["Santo Domingo"]
        }
    ]
}

async def insert_data():
    print("Iniciando inserción de datos...")
    
    # Diccionario para almacenar los países creados
    countries_dict = {}
    
    # Insertar países
    print("Insertando países...")
    for country_data in COUNTRIES:
        country = await Country.create(
            country_id=uuid.uuid4(),
            name=country_data["name"],
            code=country_data["code"]
        )
        countries_dict[country.name] = country
        print(f"  - País creado: {country.name} ({country.code})")
    
    # Insertar regiones y ciudades
    print("\nInsertando regiones y ciudades...")
    for country_name, regions in REGIONS_AND_CITIES.items():
        country = countries_dict.get(country_name)
        if not country:
            print(f"  - País no encontrado: {country_name}, saltando...")
            continue
        
        print(f"  - Para el país: {country_name}")
        for region_data in regions:
            region = await Region.create(
                region_id=uuid.uuid4(),
                name=region_data["name"],
                country_id=country.country_id
            )
            print(f"    - Región creada: {region.name}")
            
            for city_name in region_data["cities"]:
                city = await City.create(
                    city_id=uuid.uuid4(),
                    name=city_name,
                    region_id=region.region_id
                )
                print(f"      - Ciudad creada: {city.name}")
    
    print("\nInserción de datos completada con éxito!")

async def main():
    print("Inicializando conexión a la base de datos...")
    await init_db()
    
    # Verificar si ya existen países en la base de datos
    count = await Country.all().count()
    if count > 0:
        print(f"Ya existen {count} países en la base de datos.")
        response = input("¿Desea continuar con la inserción? (s/n): ")
        if response.lower() != 's':
            print("Operación cancelada.")
            return
    
    await insert_data()

if __name__ == "__main__":
    asyncio.run(main())
