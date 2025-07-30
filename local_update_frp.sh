#!/bin/bash

# Script to add store_id to factoryResetProtection table in local development environment

echo "Adding store_id to factoryResetProtection table in local development..."

# Use the local development containers
DB_CONTAINER="smartpay-db-dev"
API_CONTAINER="smartpay-db-api-dev"

echo "Using database container: $DB_CONTAINER"
echo "Using API container: $API_CONTAINER"

# Create temporary SQL file
TMP_SQL="/tmp/add_store_id_to_frp_local.sql"
cat > $TMP_SQL << 'EOF'
-- Add store_id column to factoryResetProtection table if it doesn't exist
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_name = 'factoryresetprotection'
    ) THEN
        IF NOT EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = 'factoryresetprotection' AND column_name = 'store_id'
        ) THEN
            ALTER TABLE "factoryResetProtection" ADD COLUMN store_id UUID;
            
            -- Add foreign key constraint if store table exists
            IF EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_name = 'store'
            ) THEN
                ALTER TABLE "factoryResetProtection" 
                ADD CONSTRAINT fk_factoryresetprotection_store 
                FOREIGN KEY (store_id) REFERENCES store(id);
            END IF;
            
            -- Drop existing unique constraints if they exist
            ALTER TABLE "factoryResetProtection" DROP CONSTRAINT IF EXISTS factoryresetprotection_account_id_key;
            ALTER TABLE "factoryResetProtection" DROP CONSTRAINT IF EXISTS factoryresetprotection_email_key;
            
            -- Add composite unique constraints
            ALTER TABLE "factoryResetProtection" 
            ADD CONSTRAINT factoryresetprotection_account_id_store_id_key 
            UNIQUE (account_id, store_id);
            
            ALTER TABLE "factoryResetProtection" 
            ADD CONSTRAINT factoryresetprotection_email_store_id_key 
            UNIQUE (email, store_id);
            
            RAISE NOTICE 'Added store_id column and updated constraints for factoryResetProtection table';
        ELSE
            RAISE NOTICE 'store_id column already exists in factoryResetProtection table';
        END IF;
    ELSE
        RAISE NOTICE 'factoryResetProtection table does not exist yet';
    END IF;
END $$;
EOF

# Copy SQL file to container
CONTAINER_SQL_PATH="/tmp/add_store_id_to_frp_local.sql"
echo "Copying SQL file to container..."
docker cp "$TMP_SQL" "$DB_CONTAINER:$CONTAINER_SQL_PATH"

# Execute SQL file
echo "Executing SQL file..."
docker exec "$DB_CONTAINER" psql -U postgres -d smartpay -f "$CONTAINER_SQL_PATH"

# Clean up
echo "Cleaning up temporary files..."
rm "$TMP_SQL"
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
