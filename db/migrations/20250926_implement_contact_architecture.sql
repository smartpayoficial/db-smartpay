-- ========= REVERT PREVIOUS CHANGES =========
-- Drop the columns that were added to the store table
ALTER TABLE "store"
DROP COLUMN IF EXISTS "phone_one",
DROP COLUMN IF EXISTS "phone_two",
DROP COLUMN IF EXISTS "account_number_one",
DROP COLUMN IF EXISTS "account_number_two";


-- ========= NEW ARCHITECTURE =========

-- Step 1: Add new columns to the existing 'country' table
ALTER TABLE "country"
ADD COLUMN IF NOT EXISTS "phone_code" VARCHAR(10),
ADD COLUMN IF NOT EXISTS "flag_icon_url" VARCHAR(255);


-- Step 2: Create the 'account_types' table to define each payment/contact method
CREATE TABLE IF NOT EXISTS "account_types" (
    "id" SERIAL PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL UNIQUE,
    "description" TEXT,
    "icon_url" VARCHAR(255),
    "is_international" BOOLEAN NOT NULL DEFAULT FALSE,
    "form_schema" JSONB, -- The 'recipe' to build the frontend form
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "deleted_at" TIMESTAMPTZ
);


-- Step 3: Create the 'country_account_types' join table for the many-to-many relationship
CREATE TABLE IF NOT EXISTS "country_account_types" (
    "country_id" UUID NOT NULL REFERENCES "country"("country_id") ON DELETE CASCADE,
    "account_type_id" INTEGER NOT NULL REFERENCES "account_types"("id") ON DELETE CASCADE,
    PRIMARY KEY ("country_id", "account_type_id")
);


-- Step 4: Create the 'store_contact' table to hold the actual contact/payment data for each store
CREATE TABLE IF NOT EXISTS "store_contact" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "store_id" UUID NOT NULL REFERENCES "store"("id") ON DELETE CASCADE,
    "account_type_id" INTEGER NOT NULL REFERENCES "account_types"("id") ON DELETE RESTRICT,
    "contact_details" JSONB NOT NULL, -- Stores the actual data, e.g., { "phone_number": "+57..." }
    "description" VARCHAR(100),
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "deleted_at" TIMESTAMPTZ
);


-- Step 5: Seed the 'account_types' table with some initial data
-- Note: The form_schema is a JSON string.
INSERT INTO "account_types" ("name", "description", "is_international", "form_schema") VALUES
('Phone', 'Número de teléfono de contacto', TRUE, '[{"name": "phone_number", "label": "Número de Teléfono", "type": "tel", "required": true}]'),
('Nequi', 'Cuenta de Nequi Colombia', FALSE, '[{"name": "phone_number", "label": "Número de Celular", "type": "tel", "required": true}]'),
('PayPal', 'Cuenta de PayPal', TRUE, '[{"name": "email", "label": "Email de PayPal", "type": "email", "required": true}]'),
('Bancolombia', 'Cuenta de ahorros/corriente Bancolombia', FALSE, '[{"name": "account_number", "label": "Número de Cuenta", "type": "text", "required": true}, {"name": "account_type", "label": "Tipo de Cuenta", "type": "select", "options": ["Ahorros", "Corriente"], "required": true}, {"name": "holder_name", "label": "Nombre del Titular", "type": "text", "required": true}]')
ON CONFLICT ("name") DO NOTHING;

-- Example of associating a non-international type with a country would be a separate script or done via the admin panel:
-- INSERT INTO "country_account_types" ("country_id", "account_type_id") VALUES
-- ((SELECT id FROM country WHERE name = 'Colombia'), (SELECT id FROM account_types WHERE name = 'Nequi')),
-- ((SELECT id FROM country WHERE name = 'Colombia'), (SELECT id FROM account_types WHERE name = 'Bancolombia'));
