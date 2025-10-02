-- Migration to add a category to account_types for better filtering.

-- Step 1: Create the new ENUM type for the categories.
-- Use IF NOT EXISTS to make the script safely re-runnable.
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'account_category_enum') THEN
        CREATE TYPE account_category_enum AS ENUM (
            'CONTACT',
            'BANK_ACCOUNT',
            'MOBILE_PAYMENT',
            'PAYMENT_GATEWAY',
            'PUBLIC_PROFILE',
            'WEBHOOK',
            'LOCATION'
        );
    END IF;
END$$;


-- Step 2: Add the new 'category' column to the 'account_types' table.
-- Use IF NOT EXISTS to make the script safely re-runnable.
ALTER TABLE account_types
ADD COLUMN IF NOT EXISTS category account_category_enum;


-- Step 3: Update the existing account types with their corresponding category.
-- This is idempotent, running it multiple times has the same result.
UPDATE account_types SET category = 'CONTACT' WHERE name = 'Phone';
UPDATE account_types SET category = 'MOBILE_PAYMENT' WHERE name = 'Nequi';
UPDATE account_types SET category = 'PAYMENT_GATEWAY' WHERE name = 'PayPal';
UPDATE account_types SET category = 'BANK_ACCOUNT' WHERE name = 'Bancolombia';
