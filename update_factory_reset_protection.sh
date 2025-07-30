#!/bin/bash

# Script to add store_id to factoryResetProtection table
# This script works in both local and VBPS environments

echo "Adding store_id to factoryResetProtection table..."

# Determine if we're in VBPS or local environment
if docker ps | grep -q "docker-smartpay-db-v12-1"; then
    # VBPS environment
    echo "Detected VBPS environment"
    DB_CONTAINER="docker-smartpay-db-v12-1"
    API_CONTAINER="smartpay-db-api"
else
    # Local environment
    echo "Detected local environment"
    DB_CONTAINER=$(docker ps | grep "smartpay-db-v12" | awk '{print $NF}')
    API_CONTAINER=$(docker ps | grep "smartpay-db-api" | awk '{print $NF}')
    
    if [ -z "$DB_CONTAINER" ]; then
        echo "Error: Could not find database container"
        exit 1
    fi
    
    if [ -z "$API_CONTAINER" ]; then
        echo "Error: Could not find API container"
        exit 1
    fi
fi

echo "Using database container: $DB_CONTAINER"
echo "Using API container: $API_CONTAINER"

# Ask which database to use
echo "Which database would you like to modify?"
echo "1) smartpay (default production database)"
echo "2) smartpay_dev_db (development database)"
echo "3) smartpay_test_db (test database)"
read -p "Enter your choice [1-3, default=1]: " DB_CHOICE

case $DB_CHOICE in
    2)
        DB_NAME="smartpay_dev_db"
        ;;
    3)
        DB_NAME="smartpay_test_db"
        ;;
    *)
        DB_NAME="smartpay"
        ;;
esac

echo "Using database: $DB_NAME"

# Copy SQL file to container
SQL_FILE="db/add_store_id_to_factory_reset_protection.sql"
CONTAINER_SQL_PATH="/tmp/add_store_id_to_factory_reset_protection.sql"

echo "Copying SQL file to container..."
docker cp "$SQL_FILE" "$DB_CONTAINER:$CONTAINER_SQL_PATH"

# Execute SQL file
echo "Executing SQL file..."
docker exec "$DB_CONTAINER" psql -U postgres -d "$DB_NAME" -f "$CONTAINER_SQL_PATH"

# Clean up
echo "Cleaning up temporary files..."
docker exec "$DB_CONTAINER" rm "$CONTAINER_SQL_PATH"

# Ask if user wants to restart API container
read -p "Do you want to restart the API container to apply changes? (y/n): " RESTART_API

if [[ $RESTART_API == "y" || $RESTART_API == "Y" ]]; then
    echo "Restarting API container..."
    docker restart "$API_CONTAINER"
    echo "API container restarted."
else
    echo "Skipping API container restart."
fi

echo "Factory reset protection table update completed."
