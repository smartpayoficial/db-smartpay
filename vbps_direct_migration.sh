#!/bin/bash

# Script to apply configuration table changes on VBPS by finding the actual database container
# This script should be executed on the VBPS server

echo "Applying configuration table changes on VBPS..."

# List all containers to find database containers
echo "Listing all containers to find the database..."
docker ps

echo "Please examine the container list above and enter the name of the actual database container:"
read DB_CONTAINER

if [ -z "$DB_CONTAINER" ]; then
    echo "Error: No container name provided."
    exit 1
fi

echo "Using database container: $DB_CONTAINER"

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

echo "Please enter the database name (default: smartpay):"
read DB_NAME
if [ -z "$DB_NAME" ]; then
    DB_NAME="smartpay"
fi

echo "Please enter the database user (default: postgres):"
read DB_USER
if [ -z "$DB_USER" ]; then
    DB_USER="postgres"
fi

echo "Using database: $DB_NAME with user: $DB_USER"

# Copy the SQL file to the container
echo "Copying SQL file to container..."
docker cp migration.sql $DB_CONTAINER:/migration.sql

# Execute the SQL file in the container
echo "Executing SQL in the container..."
docker exec -i $DB_CONTAINER sh -c "if command -v psql > /dev/null; then psql -U $DB_USER -d $DB_NAME -f /migration.sql; else echo 'psql not found in container'; fi"

# Check if the command was successful
if [ $? -eq 0 ]; then
    echo "Migration completed successfully for database $DB_NAME in container $DB_CONTAINER!"
    
    # Find the API container
    echo "Looking for API containers..."
    API_CONTAINER=$(docker ps | grep "smartpay.*api" | grep -v "db" | head -n 1 | awk '{print $NF}')
    
    if [ -z "$API_CONTAINER" ]; then
        echo "Could not find API container automatically."
        echo "Please enter the name of the API container to restart (leave empty to skip):"
        read API_CONTAINER
    else
        echo "Found API container: $API_CONTAINER"
    fi
    
    if [ ! -z "$API_CONTAINER" ]; then
        echo "Restarting API container..."
        docker restart $API_CONTAINER
        echo "API container restarted."
    else
        echo "Skipping API container restart."
    fi
    
    echo "All changes have been applied successfully!"
    
    # Clean up
    rm migration.sql
    docker exec $DB_CONTAINER rm -f /migration.sql
else
    echo "Migration failed for database $DB_NAME in container $DB_CONTAINER."
    echo "Let's try a different approach..."
    
    echo "Listing database container environment variables..."
    docker exec $DB_CONTAINER env | grep -i "postgres\|db\|sql"
    
    echo "Please check if there's any useful information above about the database connection."
    echo "If you see the database connection details, you can try to connect manually."
    
    # Clean up
    rm migration.sql
    docker exec $DB_CONTAINER rm -f /migration.sql
    exit 1
fi
