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
