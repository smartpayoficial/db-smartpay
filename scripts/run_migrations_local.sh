#!/bin/bash

# Configuración LOCAL
DB_USER="postgres"  # Cambiar por tu usuario local
DB_NAME="smartpay"  # Cambiar por tu DB local
DB_HOST="localhost"
MIGRATIONS_DIR="$(dirname "$0")/../db/migrations"

# Verificar dependencias locales
if ! command -v goose &> /dev/null; then
    echo "ERROR: Goose no está instalado localmente"
    echo "Ejecuta: go install github.com/pressly/goose/v3/cmd/goose@latest"
    exit 1
fi

if ! command -v psql &> /dev/null; then
    echo "ERROR: PostgreSQL client no instalado"
    echo "Instala con: sudo apt install postgresql-client"
    exit 1
fi

# Ejecutar migraciones
echo "=== EJECUTANDO MIGRACIONES LOCALES ==="
echo "Base de datos: postgresql://${DB_USER}@${DB_HOST}/${DB_NAME}"

cd "$MIGRATIONS_DIR"
"$(go env GOPATH)/bin/goose" postgres "user=${DB_USER} dbname=${DB_NAME} host=${DB_HOST} sslmode=disable" up

if [ $? -eq 0 ]; then
    echo "
=== MIGRACIONES APLICADAS CON ÉXITO ==="
    echo "Verifica los cambios con:"
    echo "psql -U ${DB_USER} -d ${DB_NAME} -c '\d store'"
else
    echo "
=== ERROR AL APLICAR MIGRACIONES ==="
    exit 1
fi
