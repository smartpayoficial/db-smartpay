#!/bin/bash

# Script para ejecutar todos los scripts de inserción de datos en la base de datos
# Autor: Cascade AI Assistant
# Fecha: $(date)

set -e  # Salir si cualquier comando falla

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes con colores
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Función para verificar si Docker está ejecutándose
check_docker() {
    if ! docker ps &> /dev/null; then
        print_message $RED "Error: Docker no está ejecutándose o no tienes permisos para acceder a él."
        print_message $YELLOW "Por favor, inicia Docker y asegúrate de tener los permisos necesarios."
        exit 1
    fi
}

# Función para verificar si el contenedor de la base de datos está ejecutándose
check_db_container() {
    if ! docker ps | grep -q "docker-smartpay-db-v12-1"; then
        print_message $RED "Error: El contenedor de la base de datos (docker-smartpay-db-v12-1) no está ejecutándose."
        print_message $YELLOW "Por favor, inicia los servicios con 'docker-compose up -d'"
        exit 1
    fi
}

# Función para verificar si el archivo existe
check_file_exists() {
    local file=$1
    if [ ! -f "$file" ]; then
        print_message $RED "Error: El archivo $file no existe."
        exit 1
    fi
}

# Función para ejecutar un script Python
run_python_script() {
    local script=$1
    local description=$2
    
    print_message $BLUE "Ejecutando: $description"
    print_message $YELLOW "Script: $script"
    
    if python3 "$script"; then
        print_message $GREEN "✓ $description completado exitosamente"
    else
        print_message $RED "✗ Error al ejecutar $description"
        exit 1
    fi
    echo ""
}

# Función para ejecutar comandos SQL directamente
run_sql_command() {
    local sql_command=$1
    local description=$2
    
    print_message $BLUE "Ejecutando: $description"
    print_message $YELLOW "SQL: $sql_command"
    
    if docker exec -i docker-smartpay-db-v12-1 psql -U postgres -d smartpay -c "$sql_command"; then
        print_message $GREEN "✓ $description completado exitosamente"
    else
        print_message $RED "✗ Error al ejecutar $description"
        exit 1
    fi
    echo ""
}

# Función principal
main() {
    print_message $GREEN "======================================================"
    print_message $GREEN "    SCRIPT DE INSERCIÓN DE DATOS - SMART PAY DB"
    print_message $GREEN "======================================================"
    echo ""
    
    # Verificaciones previas
    print_message $BLUE "Realizando verificaciones previas..."
    check_docker
    check_db_container
    
    # Verificar que los scripts existen
    check_file_exists "insert_countries_script.py"
    check_file_exists "insert_countries_orm.py"
    check_file_exists "scripts/seed_all.py"
    check_file_exists "db/insert_countries_regions_cities.sql"
    
    print_message $GREEN "✓ Todas las verificaciones pasaron correctamente"
    echo ""
    
    # Paso 1: Habilitar extensión UUID
    print_message $BLUE "=== PASO 1: Configuración inicial ==="
    run_sql_command "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";" "Habilitando extensión UUID"
    
    # Paso 2: Ejecutar script SQL de países, regiones y ciudades
    print_message $BLUE "=== PASO 2: Inserción de datos geográficos ==="
    run_python_script "insert_countries_script.py" "Insertando países, regiones y ciudades (SQL)"
    
    # Paso 3: Ejecutar script ORM alternativo (si es necesario)
    print_message $BLUE "=== PASO 3: Verificación con ORM ==="
    print_message $YELLOW "Nota: Este paso puede fallar si los datos ya existen, es normal."
    if python3 insert_countries_orm.py; then
        print_message $GREEN "✓ Script ORM ejecutado exitosamente"
    else
        print_message $YELLOW "⚠ Script ORM falló (posiblemente datos duplicados, continuando...)"
    fi
    echo ""
    
    # Paso 4: Ejecutar seed de todos los datos
    print_message $BLUE "=== PASO 4: Seed de datos adicionales ==="
    print_message $YELLOW "Nota: Asegúrate de que la API esté ejecutándose en localhost:8002"
    read -p "¿La API está ejecutándose? (y/N): " api_running
    
    if [[ $api_running =~ ^[Yy]$ ]]; then
        run_python_script "scripts/seed_all.py" "Ejecutando seed completo de datos"
    else
        print_message $YELLOW "⚠ Saltando seed de datos adicionales. Ejecuta manualmente cuando la API esté lista:"
        print_message $YELLOW "   python scripts/seed_all.py"
    fi
    
    # Paso 5: Verificación final
    print_message $BLUE "=== PASO 5: Verificación final ==="
    run_sql_command "SELECT 'Countries: ' || COUNT(*) FROM country UNION ALL SELECT 'Regions: ' || COUNT(*) FROM region UNION ALL SELECT 'Cities: ' || COUNT(*) FROM city;" "Verificando datos insertados"
    
    # Verificar tabla store si existe
    print_message $BLUE "Verificando tabla store..."
    if docker exec -i docker-smartpay-db-v12-1 psql -U postgres -d smartpay -c "SELECT COUNT(*) FROM store;" 2>/dev/null; then
        print_message $GREEN "✓ Tabla store verificada"
    else
        print_message $YELLOW "⚠ Tabla store no encontrada (puede ser normal si no se ha creado aún)"
    fi
    
    echo ""
    print_message $GREEN "======================================================"
    print_message $GREEN "    ✓ PROCESO COMPLETADO EXITOSAMENTE"
    print_message $GREEN "======================================================"
    print_message $BLUE "Resumen de lo que se ejecutó:"
    print_message $YELLOW "  • Habilitación de extensión UUID"
    print_message $YELLOW "  • Inserción de países, regiones y ciudades"
    print_message $YELLOW "  • Verificación de datos con ORM"
    print_message $YELLOW "  • Seed de datos adicionales (si la API estaba disponible)"
    print_message $YELLOW "  • Verificación final de datos"
    echo ""
    print_message $BLUE "La base de datos está lista para usar."
}

# Verificar si se está ejecutando desde el directorio correcto
if [ ! -f "insert_countries_script.py" ]; then
    print_message $RED "Error: Este script debe ejecutarse desde el directorio raíz del proyecto."
    print_message $YELLOW "Navega al directorio que contiene insert_countries_script.py"
    exit 1
fi

# Ejecutar función principal
main "$@"
