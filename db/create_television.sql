DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'television_state') THEN
        CREATE TYPE television_state AS ENUM ('Active','Inactive');
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS television (
    television_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    enrolment_id  UUID UNIQUE NOT NULL REFERENCES enrolment(enrolment_id) ON DELETE RESTRICT,
    brand           VARCHAR(50) NOT NULL,
    model           VARCHAR(100) NOT NULL,
    android_version INTEGER NOT NULL,
    serial_number   VARCHAR(100) NOT NULL UNIQUE,
    board           VARCHAR(50),
    fingerprint     VARCHAR(500),
    state           television_state NOT NULL DEFAULT 'Active',
    created_at    TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
