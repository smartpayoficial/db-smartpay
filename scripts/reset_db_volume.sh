#!/bin/bash
# Script para eliminar y recrear el volumen de la base de datos PostgreSQL

# Colores para mensajes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Reinicio completo de la base de datos ===${NC}"

# Verificar si se ejecuta con --force
if [ "$1" != "--force" ]; then
    echo -e "${RED}ADVERTENCIA: Esta acción eliminará TODOS los datos de la base de datos.${NC}"
    echo -e "${RED}Se eliminarán todas las tablas, índices, datos y el volumen de Docker.${NC}"
    read -p "¿Estás seguro de que deseas continuar? (s/N): " confirm
    if [ "$confirm" != "s" ] && [ "$confirm" != "S" ]; then
        echo "Operación cancelada."
        exit 1
    fi
fi

# Identificar el contenedor y volumen de la base de datos
DB_CONTAINER=$(docker ps --format "{{.Names}}" | grep -E 'postgres|db-v12|smartpay-db')
if [ -z "$DB_CONTAINER" ]; then
    echo -e "${RED}No se encontró ningún contenedor de base de datos en ejecución.${NC}"
    exit 1
fi

echo -e "${YELLOW}Contenedor de base de datos identificado: ${GREEN}$DB_CONTAINER${NC}"

# Obtener el nombre del volumen
DB_VOLUME=$(docker inspect $DB_CONTAINER | grep -o '"Source": "[^"]*"' | grep -o '/var/lib/docker/volumes/[^"]*' | sed 's/\/var\/lib\/docker\/volumes\///' | sed 's/_data//')
if [ -z "$DB_VOLUME" ]; then
    echo -e "${RED}No se pudo identificar el volumen de la base de datos.${NC}"
    exit 1
fi

echo -e "${YELLOW}Volumen de base de datos identificado: ${GREEN}$DB_VOLUME${NC}"

# Detener todos los contenedores que dependen de la base de datos
echo -e "${YELLOW}Deteniendo contenedores que dependen de la base de datos...${NC}"
API_CONTAINERS=$(docker ps --format "{{.Names}}" | grep -E 'api|backend')
for container in $API_CONTAINERS; do
    echo -e "Deteniendo ${GREEN}$container${NC}..."
    docker stop $container
done

# Detener el contenedor de la base de datos
echo -e "${YELLOW}Deteniendo el contenedor de la base de datos ${GREEN}$DB_CONTAINER${NC}..."
docker stop $DB_CONTAINER

# Eliminar el volumen
echo -e "${YELLOW}Eliminando el volumen ${GREEN}$DB_VOLUME${NC}..."
docker volume rm $DB_VOLUME

# Iniciar el contenedor de la base de datos (recreará el volumen)
echo -e "${YELLOW}Iniciando el contenedor de la base de datos...${NC}"
docker start $DB_CONTAINER

# Esperar a que la base de datos esté lista
echo -e "${YELLOW}Esperando a que la base de datos esté lista...${NC}"
sleep 10

# Iniciar los contenedores de la API
echo -e "${YELLOW}Iniciando los contenedores de la API...${NC}"
for container in $API_CONTAINERS; do
    echo -e "Iniciando ${GREEN}$container${NC}..."
    docker start $container
done

echo -e "${GREEN}¡Proceso completado! La base de datos ha sido reiniciada desde cero.${NC}"
echo -e "${YELLOW}Nota: Es posible que necesites ejecutar el comando para generar los esquemas:${NC}"
echo -e "${GREEN}docker exec -i smartpay-db-api python -m app.main --generate-schema${NC}"
echo -e "${YELLOW}Y para cargar datos por defecto:${NC}"
echo -e "${GREEN}docker exec -i smartpay-db-api python -m app.main --default-data${NC}"
