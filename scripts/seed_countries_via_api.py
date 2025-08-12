#!/usr/bin/env python3
"""
Seed Latin American countries via the REST API endpoint.

- Endpoint used: POST /api/v1/countries/
- Fetches existing countries first (GET /api/v1/countries/) to avoid duplicates
- Uses only Python standard library (urllib) to avoid extra dependencies

Usage:
  API_BASE_URL=http://localhost:8002 python scripts/seed_countries_via_api.py

Notes:
- Default API_BASE_URL is http://localhost:8002 if the environment variable is not provided
- The script is idempotent: it will not re-create countries that already exist (checks by code or name)
"""

import json
import os
import sys
import time
from urllib import request, error
from urllib.parse import urljoin

# List of Latin American countries (name, ISO code 2)
LATAM_COUNTRIES = [
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

DEFAULT_BASE = "http://localhost:8002"
API_BASE = os.getenv("API_BASE_URL", DEFAULT_BASE).rstrip("/")
COUNTRIES_BASE = "/api/v1/countries/"


def http_get(url: str):
    req = request.Request(url, headers={"Accept": "application/json"}, method="GET")
    with request.urlopen(req, timeout=15) as resp:
        return resp.getcode(), json.loads(resp.read().decode("utf-8"))


def http_post(url: str, payload: dict):
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    with request.urlopen(req, timeout=15) as resp:
        return resp.getcode(), json.loads(resp.read().decode("utf-8"))


def fetch_existing_countries() -> list[dict]:
    url = urljoin(API_BASE, COUNTRIES_BASE)
    try:
        status, data = http_get(url)
        if status != 200:
            print(f"[WARN] GET {url} responded with status {status}")
            return []
        if not isinstance(data, list):
            print(f"[WARN] Unexpected response format: {type(data)}")
            return []
        return data
    except error.HTTPError as e:
        print(f"[ERROR] HTTPError on GET {url}: {e.code} {e.reason}")
    except error.URLError as e:
        print(f"[ERROR] URLError on GET {url}: {e.reason}")
    except Exception as e:
        print(f"[ERROR] Unexpected error on GET {url}: {e}")
    return []


def create_country(country: dict) -> tuple[bool, dict | None]:
    url = urljoin(API_BASE, COUNTRIES_BASE)
    try:
        status, data = http_post(url, payload=country)
        if status in (200, 201):
            return True, data
        print(f"[WARN] POST {url} returned status {status}: {data}")
        return False, None
    except error.HTTPError as e:
        try:
            details = e.read().decode("utf-8")
        except Exception:
            details = str(e)
        print(f"[ERROR] HTTPError on POST {url}: {e.code} {e.reason} - {details}")
        return False, None
    except error.URLError as e:
        print(f"[ERROR] URLError on POST {url}: {e.reason}")
        return False, None
    except Exception as e:
        print(f"[ERROR] Unexpected error on POST {url}: {e}")
        return False, None


def main():
    print("== Seed Latin American Countries via API ==")
    print(f"API base: {API_BASE}")

    existing = fetch_existing_countries()
    existing_by_code = {c.get("code", "").upper(): c for c in existing}
    existing_by_name = {c.get("name", "").strip().lower(): c for c in existing}

    print(f"Found {len(existing)} existing countries in API")

    created = 0
    skipped = 0
    for entry in LATAM_COUNTRIES:
        name = entry["name"].strip()
        code = entry["code"].upper()

        if code in existing_by_code or name.lower() in existing_by_name:
            print(f"- Skipping existing: {name} ({code})")
            skipped += 1
            continue

        ok, data = create_country({"name": name, "code": code})
        if ok:
            print(f"+ Created: {data.get('name', name)} ({data.get('code', code)})")
            created += 1
        else:
            print(f"! Failed to create: {name} ({code})")
        # small delay to avoid hammering server
        time.sleep(0.05)

    print("\nSummary:")
    print(f"  Created: {created}")
    print(f"  Skipped (already existed): {skipped}")
    print("Done.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        sys.exit(130)
