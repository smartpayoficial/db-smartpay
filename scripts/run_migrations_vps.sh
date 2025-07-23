#!/bin/bash

# Configuración
DB_USER="tu_usuario"
DB_NAME="tu_base_de_datos"
DB_HOST="tu_host"
MIGRATIONS_DIR="$(dirname "$0")/../db/migrations"

# 1. Verificar e instalar dependencias
if ! command -v goose &> /dev/null; then
    echo "Instalando goose..."
    if ! command -v go &> /dev/null; then
        echo "Instalando Go..."
        sudo apt update && sudo apt install -y golang-go
    fi
    go install github.com/pressly/goose/v3/cmd/goose@latest
    export PATH="$PATH:$(go env GOPATH)/bin"
fi

if ! command -v psql &> /dev/null; then
    echo "Instalando PostgreSQL client..."
    sudo apt update && sudo apt install -y postgresql-client
fi

# 2. Hacer backup (opcional pero recomendado)
if command -v pg_dump &> /dev/null; then
    BACKUP_FILE="/tmp/db_backup_$(date +%Y%m%d_%H%M%S).sql"
    echo "Creando backup en $BACKUP_FILE"
    pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME -F c -b -v -f $BACKUP_FILE
    
    if [ ! -f "$BACKUP_FILE" ]; then
        echo "Advertencia: No se pudo crear el backup"
    fi
else
    echo "Advertencia: pg_dump no disponible, omitiendo backup"
fi

# 3. Ejecutar migraciones
echo "Aplicando migraciones desde $MIGRATIONS_DIR"
cd "$MIGRATIONS_DIR"
"$(go env GOPATH)/bin/goose" postgres "user=$DB_USER dbname=$DB_NAME host=$DB_HOST sslmode=disable" up

if [ $? -eq 0 ]; then
    echo "Migraciones aplicadas exitosamente"
    if [ -f "$BACKUP_FILE" ]; then
        echo "Backup disponible en: $BACKUP_FILE"
    fi
else
    echo "Error al aplicar migraciones"
    if [ -f "$BACKUP_FILE" ]; then
        echo "Restaurando backup..."
        pg_restore -h $DB_HOST -U $DB_USER -d $DB_NAME -c -v "$BACKUP_FILE"
    fi
    exit 1
fi
