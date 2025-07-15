-- Create store table
CREATE TABLE IF NOT EXISTS "store" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(100) NOT NULL,
    country_id UUID NOT NULL REFERENCES "country"(country_id),
    tokens_disponibles INTEGER NOT NULL DEFAULT 0,
    plan VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    back_link VARCHAR(255),
    db_link VARCHAR(255)
);

-- Create index on country_id for better query performance
CREATE INDEX idx_store_country_id ON "store"(country_id);
