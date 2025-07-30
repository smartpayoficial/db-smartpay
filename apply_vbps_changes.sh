#!/bin/bash

# Script to apply configuration table changes on VBPS
# This script should be executed on the VBPS server

echo "Applying configuration table changes on VBPS..."

# Define the database name and user for VBPS
# You may need to adjust these values based on your VBPS configuration
DB_NAME="smartpay"
DB_USER="postgres"

# SQL commands to apply the changes
SQL_COMMANDS=$(cat << 'EOF'
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
)

# Instructions for running the SQL commands on VBPS
echo "To apply these changes on your VBPS server, follow these steps:"
echo ""
echo "1. SSH into your VBPS server"
echo "2. Connect to your PostgreSQL database:"
echo "   psql -U $DB_USER -d $DB_NAME"
echo ""
echo "3. Run the following SQL commands:"
echo "----------------------------------------------"
echo "$SQL_COMMANDS"
echo "----------------------------------------------"
echo ""
echo "4. After applying the changes, restart your API service on VBPS"
echo ""
echo "Alternatively, if you have direct psql access, you can run:"
echo "psql -U $DB_USER -d $DB_NAME -c \"$SQL_COMMANDS\""
echo ""
echo "If you're using a different database name or user on VBPS,"
echo "please adjust the commands accordingly."
