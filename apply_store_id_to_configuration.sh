#!/bin/bash

# Script to add store_id column to configuration table
# This script should be executed from the project root directory

echo "Adding store_id column to configuration table..."

# Use the exact container name from docker ps
CONTAINER_NAME="docker-smartpay-db-1"

echo "Using database container: $CONTAINER_NAME"

# Execute the SQL commands directly on the database container
docker exec -i $CONTAINER_NAME psql -U postgres -d smartpay_dev_db << EOF
-- Add store_id column to configuration table if it doesn't exist
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
        
        -- Drop the unique constraint on key column
        ALTER TABLE configuration DROP CONSTRAINT IF EXISTS configuration_key_key;
        
        -- Add unique constraint for key and store_id
        ALTER TABLE configuration 
        ADD CONSTRAINT configuration_key_store_unique 
        UNIQUE (key, store_id);
        
        RAISE NOTICE 'Added store_id column to configuration table';
    ELSE
        RAISE NOTICE 'store_id column already exists in configuration table';
    END IF;
END
\$\$;
EOF

# Check if the command was successful
if [ $? -eq 0 ]; then
    echo "Migration completed successfully!"
    echo "Now you can update the model to include the store_id field."
else
    echo "Migration failed. Please check the error messages above."
    exit 1
fi

echo "Done!"
