#!/bin/bash

# Script to increase the maximum length of the value field in the configuration table
# This script should be executed from the project root directory

echo "Increasing the maximum length of the value field in the configuration table..."

# Use the exact container name from docker ps
CONTAINER_NAME="docker-smartpay-db-1"

echo "Using database container: $CONTAINER_NAME"

# Execute the SQL commands directly on the database container
docker exec -i $CONTAINER_NAME psql -U postgres -d smartpay_dev_db << EOF
-- Increase the maximum length of the value field in the configuration table
ALTER TABLE configuration ALTER COLUMN value TYPE VARCHAR(1000);
EOF

# Check if the command was successful
if [ $? -eq 0 ]; then
    echo "Migration completed successfully!"
    echo "Now you can restart the API service to apply the changes."
else
    echo "Migration failed. Please check the error messages above."
    exit 1
fi

echo "Done!"
