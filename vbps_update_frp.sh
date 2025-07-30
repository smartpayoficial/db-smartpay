#!/bin/bash

# Script to apply factory reset protection changes to VBPS environment
# This script adds store_id to factoryResetProtection table and updates constraints

echo "Applying factory reset protection changes to VBPS database..."

# Use the known container names from previous diagnostics
DB_CONTAINER="docker-smartpay-db-v12-1"
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

# Create temporary SQL file
TMP_SQL="/tmp/add_store_id_to_frp_vbps.sql"
cat > $TMP_SQL << 'EOF'
-- Add store_id column to factoryResetProtection table
ALTER TABLE "factoryResetProtection" ADD COLUMN IF NOT EXISTS store_id UUID;

-- Add foreign key constraint if store table exists
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_name = 'store'
    ) THEN
        IF NOT EXISTS (
            SELECT 1
            FROM pg_constraint
            WHERE conname = 'fk_factoryresetprotection_store'
        ) THEN
            ALTER TABLE "factoryResetProtection" 
            ADD CONSTRAINT fk_factoryresetprotection_store 
            FOREIGN KEY (store_id) REFERENCES store(id);
        END IF;
    END IF;
END $$;

-- Drop existing unique constraints if they exist
ALTER TABLE "factoryResetProtection" DROP CONSTRAINT IF EXISTS "factoryResetProtection_account_id_key";
ALTER TABLE "factoryResetProtection" DROP CONSTRAINT IF EXISTS "factoryResetProtection_email_key";

-- Add composite unique constraints
ALTER TABLE "factoryResetProtection" 
ADD CONSTRAINT factoryresetprotection_account_id_store_id_key 
UNIQUE (account_id, store_id);

ALTER TABLE "factoryResetProtection" 
ADD CONSTRAINT factoryresetprotection_email_store_id_key 
UNIQUE (email, store_id);
EOF

# Copy SQL file to container
CONTAINER_SQL_PATH="/tmp/add_store_id_to_frp_vbps.sql"
echo "Copying SQL file to container..."
docker cp "$TMP_SQL" "$DB_CONTAINER:$CONTAINER_SQL_PATH"

# Execute SQL file
echo "Executing SQL file..."
docker exec "$DB_CONTAINER" psql -U postgres -d "$DB_NAME" -f "$CONTAINER_SQL_PATH"

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
