#!/bin/bash

# Script para recrear la base de datos con los nuevos campos únicos
# Ejecutar desde el directorio raíz del proyecto

echo "🚀 Recreando base de datos con campos únicos"
echo "=============================================="

# Cambiar al directorio docker
cd docker

echo "🛑 Parando contenedores..."
docker-compose -f Docker-compose.dev.yml down

echo "🗑️  Eliminando volumen de base de datos..."
docker volume rm smartpay-db

echo "📦 Recreando volumen de base de datos..."
docker volume create smartpay-db

echo "🏗️  Construyendo e iniciando contenedores..."
docker-compose -f Docker-compose.dev.yml up --build -d

if [ $? -eq 0 ]; then
    echo "✅ Base de datos recreada exitosamente"
    echo ""
    echo "📋 Cambios aplicados:"
    echo "- enrolment_id es único por dispositivo"
    echo "- imei es único en toda la base de datos"
    echo "- imei_two es único en toda la base de datos"
    echo ""
    echo "📡 Servicios disponibles:"
    echo "- Base de datos: localhost:5437"
    echo "- API: localhost:8002"
    echo ""
    echo "⏳ Esperando que los servicios estén listos..."
    sleep 10
    docker-compose -f Docker-compose.dev.yml ps
else
    echo "❌ Error al recrear la base de datos"
    exit 1
fi
