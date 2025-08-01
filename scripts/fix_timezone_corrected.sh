#!/bin/bash

# Script para ejecutar la corrección de zona horaria en la base de datos
# Este script ejecuta el SQL corregido directamente en el contenedor de Docker

echo "Aplicando corrección de zona horaria a la base de datos..."

# Ejecutar el SQL en el contenedor de Docker
docker exec -i docker-smartpay-db-v12-1 psql -U postgres -d smartpay < scripts/fix_datetime_corrected.sql

# Verificar el resultado
if [ $? -eq 0 ]; then
    echo "Corrección aplicada correctamente."
    echo "Ahora la base de datos está configurada para usar UTC de manera consistente."
else
    echo "Error al aplicar la corrección. Verifica los logs para más detalles."
fi

echo "Proceso completado."
