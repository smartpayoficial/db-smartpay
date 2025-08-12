#!/usr/bin/env python3
"""
Seed Latin America (countries, regions, and cities where available) via the REST API.

- Endpoints used:
  - Countries: GET /api/v1/countries/ ; POST /api/v1/countries/
  - Regions:   GET /api/v1/regions?country_id=... ; POST /api/v1/regions/
  - Cities:    GET /api/v1/cities?region_id=...   ; POST /api/v1/cities/

- The script is idempotent:
  - It fetches existing entities and avoids creating duplicates (case-insensitive by name per scope)

Usage:
  API_BASE_URL=http://localhost:8002 python scripts/seed_latam_via_api.py

Notes:
- Default API_BASE_URL is http://localhost:8002 if not provided
- Only standard library is used (urllib)
"""

import json
import os
import sys
import time
from typing import Dict, List
from urllib import request, error
from urllib.parse import urlencode, urljoin

DEFAULT_BASE = "http://localhost:8002"
API_BASE = os.getenv("API_BASE_URL", DEFAULT_BASE).rstrip("/")
COUNTRIES_BASE = "/api/v1/countries/"
REGIONS_BASE = "/api/v1/regions/"
CITIES_BASE = "/api/v1/cities/"

# Countries list (ISO alpha-2 codes)
LATAM_COUNTRIES: List[Dict[str, str]] = [
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
    {"name": "Venezuela", "code": "VE"},
    {"name": "Haiti", "code": "HT"},
    {"name": "Puerto Rico", "code": "PR"},
    {"name": "Belize", "code": "BZ"},
    {"name": "Guyana", "code": "GY"},
    {"name": "Suriname", "code": "SR"},
    {"name": "French Guiana", "code": "GF"},
    {"name": "Antigua and Barbuda", "code": "AG"},
    {"name": "Bahamas", "code": "BS"},
    {"name": "Barbados", "code": "BB"},
    {"name": "Dominica", "code": "DM"},
    {"name": "Grenada", "code": "GD"},
    {"name": "Jamaica", "code": "JM"},
    {"name": "Saint Kitts and Nevis", "code": "KN"},
    {"name": "Saint Lucia", "code": "LC"},
    {"name": "Saint Vincent and the Grenadines", "code": "VC"},
    {"name": "Trinidad and Tobago", "code": "TT"},
    {"name": "Aruba", "code": "AW"},
    {"name": "Curaçao", "code": "CW"},
    {"name": "Sint Maarten", "code": "SX"},
    {"name": "Bonaire", "code": "BQ"},
    {"name": "Turks and Caicos Islands", "code": "TC"},
    {"name": "Cayman Islands", "code": "KY"},
    {"name": "British Virgin Islands", "code": "VG"},
    {"name": "U.S. Virgin Islands", "code": "VI"},
    {"name": "Guadeloupe", "code": "GP"},
    {"name": "Martinique", "code": "MQ"},
    {"name": "Saint Martin", "code": "MF"},
    {"name": "Saint Barthélemy", "code": "BL"},
    {"name": "Montserrat", "code": "MS"},
    {"name": "Anguilla", "code": "AI"},
]

# Regions and cities per country (subset where we have curated data)
REGIONS_AND_CITIES: Dict[str, List[Dict[str, List[str]]]] = {
    "Colombia": [
        {"name": "Bogotá D.C.", "cities": ["Bogotá"]},
        {"name": "Antioquia", "cities": ["Medellín", "Envigado", "Itagüí"]},
        {"name": "Valle del Cauca", "cities": ["Cali", "Palmira", "Buga"]},
        {"name": "Cundinamarca", "cities": ["Soacha", "Zipaquirá", "Chía"]},
        {"name": "Atlántico", "cities": []},
        {"name": "Santander", "cities": []},
        {"name": "Bolívar", "cities": []},
    ],
    "Mexico": [
        {"name": "Jalisco", "cities": ["Guadalajara", "Zapopan", "Tlaquepaque"]},
        {"name": "Ciudad de México", "cities": []},
        {"name": "Estado de México", "cities": ["Naucalpan de Juárez", "Ecatepec de Morelos", "Nezahualcóyotl"]},
        {"name": "Nuevo León", "cities": []},
        {"name": "Veracruz", "cities": []},
        {"name": "Puebla", "cities": []},
    ],
    "Argentina": [
        {"name": "Buenos Aires (Provincia)", "cities": ["La Plata", "Mar del Plata", "Bahía Blanca"]},
        {"name": "Ciudad Autónoma de Buenos Aires", "cities": []},
        {"name": "Córdoba", "cities": []},
        {"name": "Santa Fe", "cities": []},
    ],
    "Brazil": [
        {"name": "São Paulo", "cities": ["São Paulo", "Guarulhos", "Campinas"]},
        {"name": "Rio de Janeiro", "cities": ["Rio de Janeiro", "Niterói", "Duque de Caxias"]},
        {"name": "Minas Gerais", "cities": []},
        {"name": "Bahia", "cities": []},
    ],
    "Chile": [
        {"name": "Región Metropolitana de Santiago", "cities": ["Santiago", "Puente Alto"]},
        {"name": "Valparaíso", "cities": ["Valparaíso", "Viña del Mar"]},
    ],
    "Peru": [
        {"name": "Lima", "cities": ["Lima", "Callao"]},
        {"name": "Cusco", "cities": ["Cusco"]},
    ],
    "Ecuador": [
        {"name": "Pichincha", "cities": ["Quito"]},
        {"name": "Guayas", "cities": ["Guayaquil"]},
    ],
    "Bolivia": [
        {"name": "La Paz", "cities": ["La Paz", "El Alto"]},
        {"name": "Santa Cruz", "cities": ["Santa Cruz de la Sierra"]},
    ],
    "Uruguay": [
        {"name": "Montevideo", "cities": ["Montevideo"]},
    ],
    "Paraguay": [
        {"name": "Central", "cities": ["Asunción", "Luque"]},
    ],
    "Venezuela": [
        {"name": "Distrito Capital", "cities": ["Caracas"]},
        {"name": "Zulia", "cities": ["Maracaibo"]},
    ],
    "Costa Rica": [
        {"name": "San José", "cities": ["San José"]},
    ],
    "Panama": [
        {"name": "Panamá", "cities": ["Panamá City"]},
    ],
    "Guatemala": [
        {"name": "Guatemala", "cities": ["Guatemala City"]},
    ],
    "El Salvador": [
        {"name": "San Salvador", "cities": ["San Salvador"]},
    ],
    "Honduras": [
        {"name": "Francisco Morazán", "cities": ["Tegucigalpa"]},
    ],
    "Nicaragua": [
        {"name": "Managua", "cities": ["Managua"]},
    ],
    "Cuba": [
        {"name": "La Habana", "cities": ["Havana"]},
    ],
    "Dominican Republic": [
        {"name": "Distrito Nacional", "cities": ["Santo Domingo"]},
    ],
    "Haiti": [
        {"name": "Ouest", "cities": ["Port-au-Prince"]},
    ],
    "Puerto Rico": [
        {"name": "Región Metropolitana", "cities": ["San Juan"]},
    ],
    "Belize": [
        {"name": "Capital Region", "cities": ["Belmopan"]},
    ],
    "Guyana": [
        {"name": "Capital Region", "cities": ["Georgetown"]},
    ],
    "Suriname": [
        {"name": "Capital Region", "cities": ["Paramaribo"]},
    ],
    "French Guiana": [
        {"name": "Capital Region", "cities": ["Cayenne"]},
    ],
    "Antigua and Barbuda": [
        {"name": "Capital Region", "cities": ["Saint John's"]},
    ],
    "Bahamas": [
        {"name": "Capital Region", "cities": ["Nassau"]},
    ],
    "Barbados": [
        {"name": "Capital Region", "cities": ["Bridgetown"]},
    ],
    "Dominica": [
        {"name": "Capital Region", "cities": ["Roseau"]},
    ],
    "Grenada": [
        {"name": "Capital Region", "cities": ["St. George's"]},
    ],
    "Jamaica": [
        {"name": "Capital Region", "cities": ["Kingston"]},
    ],
    "Saint Kitts and Nevis": [
        {"name": "Capital Region", "cities": ["Basseterre"]},
    ],
    "Saint Lucia": [
        {"name": "Capital Region", "cities": ["Castries"]},
    ],
    "Saint Vincent and the Grenadines": [
        {"name": "Capital Region", "cities": ["Kingstown"]},
    ],
    "Trinidad and Tobago": [
        {"name": "Capital Region", "cities": ["Port of Spain"]},
    ],
    "Aruba": [
        {"name": "Capital Region", "cities": ["Oranjestad"]},
    ],
    "Curaçao": [
        {"name": "Capital Region", "cities": ["Willemstad"]},
    ],
    "Sint Maarten": [
        {"name": "Capital Region", "cities": ["Philipsburg"]},
    ],
    "Bonaire": [
        {"name": "Capital Region", "cities": ["Kralendijk"]},
    ],
    "Turks and Caicos Islands": [
        {"name": "Capital Region", "cities": ["Cockburn Town"]},
    ],
    "Cayman Islands": [
        {"name": "Capital Region", "cities": ["George Town"]},
    ],
    "British Virgin Islands": [
        {"name": "Capital Region", "cities": ["Road Town"]},
    ],
    "U.S. Virgin Islands": [
        {"name": "Capital Region", "cities": ["Charlotte Amalie"]},
    ],
    "Guadeloupe": [
        {"name": "Capital Region", "cities": ["Basse-Terre"]},
    ],
    "Martinique": [
        {"name": "Capital Region", "cities": ["Fort-de-France"]},
    ],
    "Saint Martin": [
        {"name": "Capital Region", "cities": ["Marigot"]},
    ],
    "Saint Barthélemy": [
        {"name": "Capital Region", "cities": ["Gustavia"]},
    ],
    "Montserrat": [
        {"name": "Capital Region", "cities": ["Brades"]},
    ],
    "Anguilla": [
        {"name": "Capital Region", "cities": ["The Valley"]},
    ],
}


def http_get(url: str):
    req = request.Request(url, headers={"Accept": "application/json"}, method="GET")
    with request.urlopen(req, timeout=20) as resp:
        return resp.getcode(), json.loads(resp.read().decode("utf-8"))


def http_post(url: str, payload: dict):
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=20) as resp:
        return resp.getcode(), json.loads(resp.read().decode("utf-8"))


def fetch_all_countries() -> List[dict]:
    url = urljoin(API_BASE, COUNTRIES_BASE)
    try:
        status, data = http_get(url)
        if status != 200 or not isinstance(data, list):
            return []
        return data
    except Exception as e:
        print(f"[ERROR] fetch_all_countries: {e}")
        return []


def ensure_country(name: str, code: str, existing_by_code: Dict[str, dict], existing_by_name: Dict[str, dict]) -> dict | None:
    code_u = code.upper()
    name_k = name.strip().lower()
    if code_u in existing_by_code:
        return existing_by_code[code_u]
    if name_k in existing_by_name:
        return existing_by_name[name_k]
    url = urljoin(API_BASE, COUNTRIES_BASE)
    try:
        status, data = http_post(url, {"name": name, "code": code_u})
        if status in (200, 201):
            return data
    except error.HTTPError as e:
        print(f"[ERROR] ensure_country HTTPError: {e.code} {e.reason}")
    except Exception as e:
        print(f"[ERROR] ensure_country: {e}")
    return None


def fetch_regions(country_id: str) -> List[dict]:
    qs = urlencode({"country_id": country_id})
    url = urljoin(API_BASE, f"{REGIONS_BASE}?{qs}")
    try:
        status, data = http_get(url)
        if status != 200 or not isinstance(data, list):
            return []
        return data
    except Exception as e:
        print(f"[ERROR] fetch_regions: {e}")
        return []


def ensure_region(name: str, country_id: str, existing_regions: Dict[str, dict]) -> dict | None:
    key = name.strip().lower()
    if key in existing_regions:
        return existing_regions[key]
    url = urljoin(API_BASE, REGIONS_BASE)
    try:
        status, data = http_post(url, {"name": name, "country_id": country_id})
        if status in (200, 201):
            return data
    except error.HTTPError as e:
        print(f"[ERROR] ensure_region HTTPError: {e.code} {e.reason}")
    except Exception as e:
        print(f"[ERROR] ensure_region: {e}")
    return None


def fetch_cities(region_id: str) -> List[dict]:
    qs = urlencode({"region_id": region_id})
    url = urljoin(API_BASE, f"{CITIES_BASE}?{qs}")
    try:
        status, data = http_get(url)
        if status != 200 or not isinstance(data, list):
            return []
        return data
    except Exception as e:
        print(f"[ERROR] fetch_cities: {e}")
        return []


def ensure_city(name: str, region_id: str, existing_cities: Dict[str, dict]) -> dict | None:
    key = name.strip().lower()
    if key in existing_cities:
        return existing_cities[key]
    url = urljoin(API_BASE, CITIES_BASE)
    try:
        status, data = http_post(url, {"name": name, "region_id": region_id})
        if status in (200, 201):
            return data
    except error.HTTPError as e:
        print(f"[ERROR] ensure_city HTTPError: {e.code} {e.reason}")
    except Exception as e:
        print(f"[ERROR] ensure_city: {e}")
    return None


def main():
    print("== Seed LATAM (countries, regions, cities) via API ==")
    print(f"API base: {API_BASE}")

    # 1) Ensure countries
    existing_countries = fetch_all_countries()
    by_code = {c.get("code", "").upper(): c for c in existing_countries}
    by_name = {c.get("name", "").strip().lower(): c for c in existing_countries}

    print(f"Found {len(existing_countries)} countries in API before seeding")

    country_objects: Dict[str, dict] = {}
    for c in LATAM_COUNTRIES:
        name = c["name"].strip()
        code = c["code"].upper()
        obj = ensure_country(name, code, by_code, by_name)
        if obj is None:
            print(f"! Failed ensuring country: {name} ({code})")
        else:
            country_objects[name] = obj
            # Update local caches
            by_code[obj.get("code", code).upper()] = obj
            by_name[obj.get("name", name).strip().lower()] = obj
            print(f"+ Country OK: {obj.get('name', name)} ({obj.get('code', code)})")
        time.sleep(0.03)

    # 2) Regions and cities
    print("\n== Seeding regions and cities ==")
    for country_name, regions in REGIONS_AND_CITIES.items():
        country = country_objects.get(country_name) or by_name.get(country_name.strip().lower())
        if not country:
            print(f"[WARN] Country not found in API, skipping regions: {country_name}")
            continue
        country_id = country.get("country_id")
        if not country_id:
            print(f"[WARN] Country has no ID, skipping: {country_name}")
            continue

        # fetch existing regions for this country
        existing_regions_list = fetch_regions(country_id)
        existing_regions = {r.get("name", "").strip().lower(): r for r in existing_regions_list}
        print(f"- {country_name}: {len(existing_regions_list)} existing regions")

        for reg in regions:
            r_name = reg["name"].strip()
            region_obj = ensure_region(r_name, country_id, existing_regions)
            if region_obj is None:
                print(f"  ! Failed ensuring region: {r_name}")
                continue
            existing_regions[r_name.lower()] = region_obj
            print(f"  + Region OK: {region_obj.get('name', r_name)}")
            time.sleep(0.03)

            # cities for this region
            region_id = region_obj.get("region_id")
            existing_cities_list = fetch_cities(region_id)
            existing_cities = {ct.get("name", "").strip().lower(): ct for ct in existing_cities_list}
            for city_name in reg.get("cities", []):
                c_name = city_name.strip()
                city_obj = ensure_city(c_name, region_id, existing_cities)
                if city_obj is None:
                    print(f"    ! Failed ensuring city: {c_name}")
                else:
                    existing_cities[c_name.lower()] = city_obj
                    print(f"    + City OK: {city_obj.get('name', c_name)}")
                time.sleep(0.02)

    print("\nDone seeding LATAM.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        sys.exit(130)
