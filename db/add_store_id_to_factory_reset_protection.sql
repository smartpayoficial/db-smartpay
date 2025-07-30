-- Add store_id column to factoryResetProtection table if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'factoryresetprotection' AND column_name = 'store_id'
    ) THEN
        ALTER TABLE "factoryResetProtection" ADD COLUMN store_id UUID;
        
        -- Add foreign key constraint
        ALTER TABLE "factoryResetProtection" 
        ADD CONSTRAINT fk_factoryresetprotection_store 
        FOREIGN KEY (store_id) REFERENCES store(id);
        
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
END $$;
