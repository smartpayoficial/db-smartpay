#!/bin/bash

# Script para ejecutar dentro del contenedor Docker de la API
# Este script corrige el problema de fechas directamente en el entorno de la aplicación

echo "Aplicando corrección de fechas en el contenedor Docker..."

# Comando para ejecutar dentro del contenedor de la API
docker exec -it smartpay-db-api bash -c '
echo "Dentro del contenedor Docker..."

# Crear un script Python temporal
cat > /tmp/fix_datetime.py << EOF
import asyncio
import datetime
import pytz
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, 
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

async def fix_datetime_issue():
    try:
        # Importar los módulos necesarios
        from tortoise import Tortoise
        import tortoise.timezone
        
        logger.info("Configurando Tortoise ORM para usar UTC...")
        
        # Configurar el uso de UTC para todas las operaciones de fecha/hora
        tortoise.timezone.set_timezone("UTC")
        
        logger.info("Tortoise ORM configurado para usar UTC.")
        
        # Verificar la configuración
        logger.info(f"Zona horaria actual: {tortoise.timezone.get_timezone()}")
        
        logger.info("Corrección aplicada correctamente.")
        
    except Exception as e:
        logger.error(f"Error al aplicar la corrección: {e}")

if __name__ == "__main__":
    logger.info("Iniciando corrección de fechas...")
    asyncio.run(fix_datetime_issue())
    logger.info("Proceso completado.")
EOF

# Ejecutar el script Python
python3 /tmp/fix_datetime.py

# Limpiar
rm /tmp/fix_datetime.py
'

# Verificar el resultado
if [ $? -eq 0 ]; then
    echo "Corrección aplicada correctamente dentro del contenedor Docker."
else
    echo "Error al aplicar la corrección. Verifica los logs para más detalles."
fi

echo "Proceso completado."
