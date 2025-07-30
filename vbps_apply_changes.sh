#!/bin/bash

# Targeted migration script for VBPS environment
# Based on diagnostic results

echo "Applying configuration table changes to VBPS database..."

# Database container and connection details from diagnostic
DB_CONTAINER="docker-smartpay-db-v12-1"
DB_USER="postgres"
DB_PASSWORD="postgres"
API_CONTAINER="smartpay-db-api"

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

# Create SQL file with migration commands
echo "Creating SQL migration file..."
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

# Copy SQL file to the database container
echo "Copying SQL file to database container..."
docker cp migration.sql $DB_CONTAINER:/tmp/migration.sql

# Execute the SQL file in the database container
echo "Executing SQL migration in database container..."
docker exec -i $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -f /tmp/migration.sql

# Check if the command was successful
if [ $? -eq 0 ]; then
    echo "Migration completed successfully for database $DB_NAME!"
    
    # Ask if the API container should be restarted
    read -p "Do you want to restart the API container ($API_CONTAINER)? [y/N]: " RESTART_API
    
    if [[ "$RESTART_API" =~ ^[Yy]$ ]]; then
        echo "Restarting API container..."
        docker restart $API_CONTAINER
        echo "API container restarted."
    else
        echo "Skipping API container restart."
    fi
    
    echo "All changes have been applied successfully!"
else
    echo "Migration failed for database $DB_NAME. Please check the error messages above."
    exit 1
fi

# Clean up
echo "Cleaning up temporary files..."
rm -f migration.sql
docker exec -i $DB_CONTAINER rm -f /tmp/migration.sql

echo "Done!"
