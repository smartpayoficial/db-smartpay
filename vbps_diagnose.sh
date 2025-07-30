#!/bin/bash

# Diagnostic script to identify database containers and connection details
# This script should be executed on the VBPS server

echo "=== SMARTPAY VBPS DIAGNOSTIC TOOL ==="
echo "This script will help identify your database container and connection details"
echo "=============================================="

echo -e "\n1. LISTING ALL RUNNING CONTAINERS:"
docker ps
echo "=============================================="

echo -e "\n2. LOOKING FOR DATABASE-RELATED CONTAINERS:"
docker ps | grep -E 'postgres|db|sql|database'
echo "=============================================="

echo -e "\n3. CHECKING DOCKER NETWORKS:"
docker network ls
echo "=============================================="

echo -e "\n4. CHECKING CONTAINER DETAILS FOR POTENTIAL DATABASE CONTAINERS:"
# Find potential database containers
DB_CONTAINERS=$(docker ps --format "{{.Names}}" | grep -E 'postgres|db|sql|database')

if [ -z "$DB_CONTAINERS" ]; then
    echo "No potential database containers found."
    echo "Let's check all containers for database-related environment variables:"
    
    ALL_CONTAINERS=$(docker ps --format "{{.Names}}")
    for CONTAINER in $ALL_CONTAINERS; do
        echo -e "\nChecking container: $CONTAINER"
        echo "Environment variables:"
        docker exec -i $CONTAINER env 2>/dev/null | grep -E 'postgres|db|sql|database|POSTGRES|DB|SQL|DATABASE' || echo "No database-related environment variables found"
        
        # Check if container has common database ports exposed
        echo "Exposed ports:"
        docker port $CONTAINER 2>/dev/null | grep -E '5432|3306|1433|27017' || echo "No common database ports exposed"
        
        # Check if container has psql command
        echo "Database tools:"
        docker exec -i $CONTAINER which psql 2>/dev/null || echo "psql not found"
        docker exec -i $CONTAINER which pg_isready 2>/dev/null || echo "pg_isready not found"
    done
else
    for CONTAINER in $DB_CONTAINERS; do
        echo -e "\nExamining container: $CONTAINER"
        
        echo "Container details:"
        docker inspect $CONTAINER --format 'ID: {{.Id}}\nImage: {{.Config.Image}}\nCommand: {{.Config.Cmd}}\nCreated: {{.Created}}\nStatus: {{.State.Status}}'
        
        echo -e "\nEnvironment variables:"
        docker exec -i $CONTAINER env 2>/dev/null | grep -E 'postgres|db|sql|database|POSTGRES|DB|SQL|DATABASE' || echo "No database-related environment variables found"
        
        echo -e "\nExposed ports:"
        docker port $CONTAINER || echo "No ports exposed"
        
        echo -e "\nNetwork settings:"
        docker inspect $CONTAINER --format 'Networks: {{range $net, $conf := .NetworkSettings.Networks}}{{$net}} (IP: {{$conf.IPAddress}}) {{end}}'
        
        echo -e "\nVolumes:"
        docker inspect $CONTAINER --format '{{range .Mounts}}{{.Source}} -> {{.Destination}} ({{.Type}}){{"\n"}}{{end}}'
        
        echo -e "\nChecking for PostgreSQL:"
        docker exec -i $CONTAINER which psql 2>/dev/null || echo "psql not found"
        docker exec -i $CONTAINER pg_isready 2>/dev/null || echo "pg_isready not found or failed"
        
        # Try to list databases if psql is available
        if docker exec -i $CONTAINER which psql &>/dev/null; then
            echo -e "\nAttempting to list databases:"
            docker exec -i $CONTAINER psql -U postgres -l 2>/dev/null || echo "Failed to list databases with postgres user"
            docker exec -i $CONTAINER psql -U postgres -c "SELECT datname FROM pg_database WHERE datname LIKE 'smartpay%';" 2>/dev/null || echo "Failed to query databases"
        fi
    done
fi

echo -e "\n5. CHECKING API CONTAINERS:"
API_CONTAINERS=$(docker ps --format "{{.Names}}" | grep -E 'api|web|app')
if [ -z "$API_CONTAINERS" ]; then
    echo "No API containers found."
else
    for CONTAINER in $API_CONTAINERS; do
        echo -e "\nExamining API container: $CONTAINER"
        echo "Environment variables related to database:"
        docker exec -i $CONTAINER env 2>/dev/null | grep -E 'postgres|db|sql|database|POSTGRES|DB|SQL|DATABASE' || echo "No database-related environment variables found"
    done
fi

echo -e "\n=============================================="
echo "DIAGNOSTIC SUMMARY:"
echo "Based on the information above, you should be able to identify:"
echo "1. Which container is running your PostgreSQL database"
echo "2. The database name, user, and connection details"
echo "3. Which API container needs to be restarted after migration"
echo "=============================================="
echo -e "\nNEXT STEPS:"
echo "1. Use the information from this diagnostic to run the migration script"
echo "2. If you found a database container with psql available, you can run:"
echo "   docker exec -i [CONTAINER_NAME] psql -U [DB_USER] -d [DB_NAME] -f /path/to/migration.sql"
echo "3. Otherwise, you may need to use a different approach to connect to your database"
echo "=============================================="
