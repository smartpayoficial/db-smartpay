#!/bin/bash

# Script to apply configuration table changes on VBPS using a temporary PostgreSQL container
# This script should be executed on the VBPS server

echo "Applying configuration table changes on VBPS using a temporary PostgreSQL container..."

# Find the database container to get connection information
echo "Looking for database containers..."
DB_CONTAINER=$(docker ps | grep "smartpay.*db" | head -n 1 | awk '{print $NF}')

if [ -z "$DB_CONTAINER" ]; then
    echo "Error: Could not find any database containers. Make sure the containers are running."
    exit 1
fi

echo "Found database container: $DB_CONTAINER"

# Get the database container's network
NETWORK=$(docker inspect $DB_CONTAINER --format '{{range $net, $conf := .NetworkSettings.Networks}}{{$net}}{{end}}')
echo "Using network: $NETWORK"

# Get the database container's IP
DB_IP=$(docker inspect $DB_CONTAINER --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}')
echo "Database container IP: $DB_IP"

# Create SQL file
echo "Creating SQL file..."
cat > migration.sql << 'EOF'
-- Check if store_id column exists and add it if it doesn't
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'configuration' AND column_name = 'store_id'
    ) THEN
        ALTER TABLE configuration ADD COLUMN store_id UUID;
        
        -- Add foreign key constraint
        ALTER TABLE configuration 
        ADD CONSTRAINT fk_configuration_store 
        FOREIGN KEY (store_id) 
        REFERENCES store(id);
        
        -- Drop the unique constraint on key column if it exists
        ALTER TABLE configuration DROP CONSTRAINT IF EXISTS configuration_key_key;
        
        -- Add unique constraint for key and store_id
        ALTER TABLE configuration 
        ADD CONSTRAINT configuration_key_store_unique 
        UNIQUE (key, store_id);
        
        RAISE NOTICE 'Added store_id column to configuration table';
    ELSE
        RAISE NOTICE 'store_id column already exists in configuration table';
    END IF;
    
    -- Increase the maximum length of the value field
    ALTER TABLE configuration ALTER COLUMN value TYPE VARCHAR(1000);
    RAISE NOTICE 'Increased value column length to 1000 characters';
END
$$;
EOF

# Try to determine the database name and port
echo "Checking environment variables in the database container..."
DB_ENV=$(docker inspect $DB_CONTAINER --format '{{range .Config.Env}}{{.}}{{"\n"}}{{end}}')
DB_NAME=$(echo "$DB_ENV" | grep POSTGRES_DB | cut -d= -f2)
DB_USER=$(echo "$DB_ENV" | grep POSTGRES_USER | cut -d= -f2)
DB_PASSWORD=$(echo "$DB_ENV" | grep POSTGRES_PASSWORD | cut -d= -f2)

# If not found in environment variables, use defaults
if [ -z "$DB_NAME" ]; then
    echo "Database name not found in environment variables, using default 'smartpay'"
    DB_NAME="smartpay"
else
    echo "Found database name: $DB_NAME"
fi

if [ -z "$DB_USER" ]; then
    echo "Database user not found in environment variables, using default 'postgres'"
    DB_USER="postgres"
else
    echo "Found database user: $DB_USER"
fi

if [ -z "$DB_PASSWORD" ]; then
    echo "Database password not found in environment variables, using empty password"
    DB_PASSWORD=""
else
    echo "Found database password (not shown)"
fi

# Get the database port
DB_PORT=$(docker inspect $DB_CONTAINER --format '{{range $p, $conf := .NetworkSettings.Ports}}{{if eq $p "5432/tcp"}}{{range $conf}}{{.HostPort}}{{end}}{{end}}{{end}}')
if [ -z "$DB_PORT" ]; then
    echo "Database port not found, using default 5432"
    DB_PORT="5432"
else
    echo "Found database port: $DB_PORT"
fi

echo "Running migration using a temporary PostgreSQL client container..."
echo "Connecting to database $DB_NAME on $DB_IP:5432 as user $DB_USER"

# Run a temporary PostgreSQL container to execute the SQL
docker run --rm -v $(pwd)/migration.sql:/migration.sql --network $NETWORK postgres:12 psql -h $DB_IP -p 5432 -U $DB_USER -d $DB_NAME -f /migration.sql

# Check if the command was successful
if [ $? -eq 0 ]; then
    echo "Migration completed successfully for database $DB_NAME!"
    
    # Find the API container
    echo "Looking for API containers..."
    API_CONTAINER=$(docker ps | grep "smartpay.*api" | grep -v "db" | head -n 1 | awk '{print $NF}')
    
    if [ -z "$API_CONTAINER" ]; then
        echo "Could not find API container. You may need to restart it manually."
    else
        echo "Found API container: $API_CONTAINER"
        echo "Restarting API container..."
        docker restart $API_CONTAINER
        echo "API container restarted."
    fi
    
    echo "All changes have been applied successfully!"
    
    # Clean up
    rm migration.sql
else
    echo "Migration failed for database $DB_NAME. Please check the error messages above."
    exit 1
fi
