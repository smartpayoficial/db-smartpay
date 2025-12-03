ALTER TABLE plan
    ADD COLUMN television_id UUID REFERENCES television(television_id) ON DELETE RESTRICT;

-- Si quieres permitir que device_id también sea opcional:
ALTER TABLE plan
    ALTER COLUMN device_id DROP NOT NULL;

ALTER TABLE plan
    ADD CONSTRAINT chk_plan_device_or_tv CHECK (
        ((device_id IS NOT NULL)::int + (television_id IS NOT NULL)::int) = 1
    );


CREATE INDEX IF NOT EXISTS idx_plan_television ON plan(television_id);

-- Agregar columna para televisor
ALTER TABLE location
    ADD COLUMN television_id UUID REFERENCES television(television_id) ON DELETE CASCADE;

-- Hacer opcional device_id
ALTER TABLE location
    ALTER COLUMN device_id DROP NOT NULL;

-- Constraint para permitir SOLO uno de los dos
ALTER TABLE location
    ADD CONSTRAINT chk_location_device_or_tv CHECK (
        ((device_id IS NOT NULL)::int + (television_id IS NOT NULL)::int) = 1
    );

-- Índices
CREATE INDEX IF NOT EXISTS idx_location_device ON location(device_id);

-- Agregar columna para televisores
ALTER TABLE payment
    ADD COLUMN television_id UUID REFERENCES television(television_id) ON DELETE RESTRICT;

-- Hacer device_id opcional
ALTER TABLE payment
    ALTER COLUMN device_id DROP NOT NULL;

-- Constraint para permitir SOLO uno (device o television)
ALTER TABLE payment
    ADD CONSTRAINT chk_payment_device_or_tv CHECK (
        ((device_id IS NOT NULL)::int + (television_id IS NOT NULL)::int) = 1
    );

-- Índices
CREATE INDEX IF NOT EXISTS idx_payment_television ON payment(television_id);

-- Agregar columna para televisores
ALTER TABLE action
    ADD COLUMN television_id UUID REFERENCES television(television_id) ON DELETE RESTRICT;

-- Hacer device_id opcional
ALTER TABLE action
    ALTER COLUMN device_id DROP NOT NULL;

-- Constraint para permitir SOLO uno (device o television)
ALTER TABLE action
    ADD CONSTRAINT chk_payment_device_or_tv CHECK (
        ((device_id IS NOT NULL)::int + (television_id IS NOT NULL)::int) = 1
    );

-- Índices
CREATE INDEX IF NOT EXISTS idx_action_television ON action(television_id);
