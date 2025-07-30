#!/bin/bash

# Script to fix the configuration table structure
# This script should be executed from the project root directory

echo "Fixing configuration table structure..."

# Find all running database containers
echo "Looking for database containers..."
DB_CONTAINERS=$(docker ps | grep "smartpay.*db" | awk '{print $NF}')

if [ -z "$DB_CONTAINERS" ]; then
    echo "Error: Could not find any database containers. Make sure the containers are running."
    exit 1
fi

echo "Found database containers:"
echo "$DB_CONTAINERS"

# Execute the SQL commands on each database container
for CONTAINER in $DB_CONTAINERS; do
    echo "Applying migration to container: $CONTAINER"
    
    # Get the list of databases in the container
    DATABASES=$(docker exec -i $CONTAINER psql -U postgres -t -c "SELECT datname FROM pg_database WHERE datname LIKE 'smartpay%';")
    
    if [ -z "$DATABASES" ]; then
        echo "No smartpay databases found in container $CONTAINER"
        continue
    fi
    
    echo "Found databases: $DATABASES"
    
    # Apply migration to each database
    for DB in $DATABASES; do
        DB=$(echo $DB | tr -d ' ')
        echo "Applying migration to database: $DB in container $CONTAINER"
        
        docker exec -i $CONTAINER psql -U postgres -d $DB << EOF
-- Check if store_id column exists and add it if it doesn't
DO \$\$
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
\$\$;
EOF
        
        # Check if the command was successful
        if [ $? -eq 0 ]; then
            echo "Migration completed successfully for database $DB in container $CONTAINER!"
        else
            echo "Migration failed for database $DB in container $CONTAINER. Please check the error messages above."
        fi
    done
done

echo "All migrations completed!"
echo "Now restart all API services to apply the changes."
