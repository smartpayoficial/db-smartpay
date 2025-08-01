#!/bin/bash
# Script para listar los contenedores Docker y sus detalles

echo "=== Contenedores en ejecución ==="
docker ps --format "ID: {{.ID}}\nNombre: {{.Names}}\nImagen: {{.Image}}\nPuertos: {{.Ports}}\nEstado: {{.Status}}\n"

echo -e "\n=== Variables de entorno del contenedor de la aplicación ==="
echo "Ejecuta el siguiente comando para ver las variables de entorno (reemplaza CONTAINER_ID con el ID del contenedor):"
echo "docker exec CONTAINER_ID env | grep -E 'POSTGRES|DB_'"

echo -e "\n=== Instrucciones para ejecutar el script SQL ==="
echo "Para ejecutar el script SQL, usa:"
echo "docker exec -i CONTAINER_ID psql -U USUARIO_DB -d NOMBRE_DB < scripts/drop_tables.sql"
echo "Reemplaza CONTAINER_ID, USUARIO_DB y NOMBRE_DB con los valores correctos."
