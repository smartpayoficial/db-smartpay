-- Add store_id column to configuration table
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
