#!/bin/bash

# Script to apply configuration table changes on VBPS using Docker
# This script should be executed on the VBPS server

echo "Applying configuration table changes on VBPS using Docker..."

# Find the database container
echo "Looking for database containers..."
DB_CONTAINER=$(docker ps | grep "smartpay.*db" | head -n 1 | awk '{print $NF}')

if [ -z "$DB_CONTAINER" ]; then
    echo "Error: Could not find any database containers. Make sure the containers are running."
    exit 1
fi

echo "Found database container: $DB_CONTAINER"

# Get the database name
echo "Getting database name..."
DATABASES=$(docker exec -i $DB_CONTAINER sh -c "psql -U postgres -l | grep smartpay" | awk '{print $1}')

if [ -z "$DATABASES" ]; then
    echo "No smartpay databases found in container $DB_CONTAINER"
    echo "Using default database name 'smartpay'"
    DB_NAME="smartpay"
else
    # Use the first database found
    DB_NAME=$(echo "$DATABASES" | head -n 1)
    echo "Using database: $DB_NAME"
fi

echo "Applying migration to database: $DB_NAME in container $DB_CONTAINER"

# Execute the SQL commands
docker exec -i $DB_CONTAINER psql -U postgres -d $DB_NAME << 'EOF'
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

# Check if the command was successful
if [ $? -eq 0 ]; then
    echo "Migration completed successfully for database $DB_NAME in container $DB_CONTAINER!"
    
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
else
    echo "Migration failed for database $DB_NAME in container $DB_CONTAINER. Please check the error messages above."
    exit 1
fi
