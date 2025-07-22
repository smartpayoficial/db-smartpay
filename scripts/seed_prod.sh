#!/bin/bash

# Versión flexible para ejecutar dentro o fuera de contenedor

# Verificar si estamos en un contenedor Docker
if [ -f /.dockerenv ] || [ -f /run/.containerenv ]; then
    echo "=== Ejecutando dentro de contenedor Docker ==="
    pip install -q httpx
    python /app/scripts/seed_all.py
else
    echo "=== Ejecutando en entorno local ==="
    echo "1. Configurando entorno virtual..."
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
    fi
    
    echo "2. Activando venv e instalando dependencias..."
    source .venv/bin/activate
    pip install -q httpx
    
    echo "3. Ejecutando script de seeding..."
    python3 scripts/seed_all.py
    
    echo "=== Completado ==="
fi
