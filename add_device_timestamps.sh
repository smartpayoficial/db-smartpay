#!/bin/bash

# Script to add timestamp columns to the device table
# Can be executed from the project root directory regardless of its location

echo "🕒 Adding timestamp columns to device table"
echo "=============================================="

# Get the current directory (project root)
PROJECT_ROOT=$(pwd)
echo "📂 Project root: $PROJECT_ROOT"

# Check if Docker Compose file exists
if [ ! -f "$PROJECT_ROOT/docker/Docker-compose.dev.yml" ] && [ ! -f "$PROJECT_ROOT/docker/Docker-compose.yml" ]; then
    echo "❌ Error: Docker Compose file not found in $PROJECT_ROOT/docker/"
    exit 1
fi

# Determine which Docker Compose file to use (dev or prod)
DOCKER_COMPOSE_FILE="Docker-compose.dev.yml"
if [ ! -f "$PROJECT_ROOT/docker/$DOCKER_COMPOSE_FILE" ]; then
    DOCKER_COMPOSE_FILE="Docker-compose.yml"
fi
echo "📄 Using Docker Compose file: $DOCKER_COMPOSE_FILE"

# Execute the SQL command to add the timestamp columns
echo "🔄 Adding created_at and updated_at columns to device table..."
docker-compose -f "$PROJECT_ROOT/docker/$DOCKER_COMPOSE_FILE" exec -T smartpay-db psql -U postgres -d smartpay_dev_db -c "
-- Check if columns already exist before adding them
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='device' AND column_name='created_at') THEN
        ALTER TABLE device ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
        RAISE NOTICE 'Added created_at column';
    ELSE
        RAISE NOTICE 'created_at column already exists';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='device' AND column_name='updated_at') THEN
        ALTER TABLE device ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
        RAISE NOTICE 'Added updated_at column';
    ELSE
        RAISE NOTICE 'updated_at column already exists';
    END IF;
END
\$\$;"

# Check if the command was successful
if [ $? -eq 0 ]; then
    echo "✅ Timestamp columns added successfully to device table"
    echo ""
    echo "📋 Changes applied:"
    echo "- created_at column added with default value of current timestamp"
    echo "- updated_at column added with default value of current timestamp"
    echo ""
    echo "🔍 Verifying columns..."
    docker-compose -f "$PROJECT_ROOT/docker/$DOCKER_COMPOSE_FILE" exec -T smartpay-db psql -U postgres -d smartpay_dev_db -c "
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name='device' AND column_name IN ('created_at', 'updated_at');"
else
    echo "❌ Error adding timestamp columns"
    exit 1
fi
