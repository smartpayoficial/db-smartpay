#!/bin/bash
# Script to apply store table to production database
# Usage: ./apply_store_table.sh [container_name] [database_name]

set -e  # Exit immediately if a command exits with a non-zero status

# Default values
CONTAINER_NAME=${1:-"docker-smartpay-db-1"}
DATABASE_NAME=${2:-"smartpay_test_db"}

echo "=== Applying store table to database ==="
echo "Container: $CONTAINER_NAME"
echo "Database: $DATABASE_NAME"
echo "=== Starting execution ==="

# Check if the container exists
if ! docker ps | grep -q "$CONTAINER_NAME"; then
  echo "Error: Container $CONTAINER_NAME not found"
  echo "Available containers:"
  docker ps
  exit 1
fi

# Execute the SQL script
echo "Executing SQL script..."
cat "$(dirname "$0")/db/add_store_table.sql" | docker exec -i "$CONTAINER_NAME" psql -U postgres -d "$DATABASE_NAME"

# Verify the table was created
echo "Verifying table creation..."
docker exec -i "$CONTAINER_NAME" psql -U postgres -d "$DATABASE_NAME" -c "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'store');"

echo "=== Execution completed ==="
echo "The store table has been applied to your database."
echo "You can now use the API endpoints at /api/v1/stores"
