-- =========================================================
-- SmartPay DB - FULL CREATE / REPAIR SCRIPT (IDEMPOTENTE)
-- PostgreSQL 13+
-- =========================================================

-- Extensión para UUID aleatorio
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- =======================
--  ENUMS
-- =======================
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_state') THEN
        CREATE TYPE user_state AS ENUM ('Active','Inactive','Initial');
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'device_state') THEN
        CREATE TYPE device_state AS ENUM ('Active','Inactive');
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'television_state') THEN
        CREATE TYPE television_state AS ENUM ('Active','Inactive');
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'payment_state') THEN
        CREATE TYPE payment_state AS ENUM ('Pending','Approved','Rejected','Failed','Returned');
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'action_state') THEN
        CREATE TYPE action_state AS ENUM ('applied','pending','failed');
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'action_type') THEN
        CREATE TYPE action_type AS ENUM ('block','locate','refresh');
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'frp_state') THEN
        CREATE TYPE frp_state AS ENUM ('Active','Inactive');
    END IF;
END $$;

-- =======================
--  TABLAS BASE (sin ciclos)
-- =======================

-- country
CREATE TABLE IF NOT EXISTS country (
    country_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name       VARCHAR(100) NOT NULL,
    code       VARCHAR(3)   NOT NULL
);

-- region
CREATE TABLE IF NOT EXISTS region (
    region_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name       VARCHAR(100) NOT NULL,
    country_id UUID NOT NULL REFERENCES country(country_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_region_country ON region(country_id);

-- city
CREATE TABLE IF NOT EXISTS city (
    city_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name      VARCHAR(100) NOT NULL,
    region_id UUID NOT NULL REFERENCES region(region_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_city_region ON city(region_id);

-- role
CREATE TABLE IF NOT EXISTS role (
    role_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(50)  NOT NULL,
    description VARCHAR(255) NOT NULL
);

-- store (admin_id se añade luego para evitar ciclo con "user")
CREATE TABLE IF NOT EXISTS store (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre             VARCHAR(100) NOT NULL,
    country_id         UUID NOT NULL REFERENCES country(country_id) ON DELETE RESTRICT,
    tokens_disponibles INTEGER NOT NULL DEFAULT 0,
    plan               VARCHAR(50) NOT NULL,
    created_at         TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at         TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    back_link          VARCHAR(255),
    db_link            VARCHAR(255)
);
CREATE INDEX IF NOT EXISTS idx_store_country ON store(country_id);

-- =======================
--  USER y dependientes
-- =======================

-- user
CREATE TABLE IF NOT EXISTS "user" (
    user_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    city_id          UUID NOT NULL REFERENCES city(city_id) ON DELETE RESTRICT,
    store_id         UUID REFERENCES store(id) ON DELETE SET NULL,
    dni              VARCHAR(16) NOT NULL,
    first_name       VARCHAR(40) NOT NULL,
    middle_name      VARCHAR(40),
    last_name        VARCHAR(40) NOT NULL,
    second_last_name VARCHAR(40),
    email            VARCHAR(80) NOT NULL,
    prefix           VARCHAR(4)  NOT NULL,
    phone            VARCHAR(15) NOT NULL,
    address          VARCHAR(255) NOT NULL,
    username         VARCHAR(50) UNIQUE NOT NULL,
    password         VARCHAR(255) NOT NULL,
    role_id          UUID NOT NULL REFERENCES role(role_id) ON DELETE RESTRICT,
    state            user_state NOT NULL DEFAULT 'Active',
    created_at       TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_user_store_dni UNIQUE (store_id, dni)
);
CREATE INDEX IF NOT EXISTS idx_user_store ON "user"(store_id);
CREATE INDEX IF NOT EXISTS idx_user_city ON "user"(city_id);
CREATE INDEX IF NOT EXISTS idx_user_role ON "user"(role_id);

-- configuration (modelo usa UUID "sueltos"; FK opcional)
CREATE TABLE IF NOT EXISTS configuration (
    configuration_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key              VARCHAR(50)   NOT NULL,
    value            VARCHAR(1000) NOT NULL,
    description      VARCHAR(255)  NOT NULL,
    store_id         UUID,
    CONSTRAINT configuration_key_store_unique UNIQUE (key, store_id)
);
/*
-- Si quieres FK dura:
ALTER TABLE configuration
  ADD CONSTRAINT IF NOT EXISTS fk_configuration_store
  FOREIGN KEY (store_id) REFERENCES store(id) ON DELETE CASCADE;
*/

-- enrolment
CREATE TABLE IF NOT EXISTS enrolment (
    enrolment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id      UUID NOT NULL REFERENCES "user"(user_id) ON DELETE RESTRICT,
    vendor_id    UUID NOT NULL REFERENCES "user"(user_id) ON DELETE RESTRICT,
    created_at   TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_enrolment_user ON enrolment(user_id);
CREATE INDEX IF NOT EXISTS idx_enrolment_vendor ON enrolment(vendor_id);

-- device (OneToOne enrolment)
CREATE TABLE IF NOT EXISTS device (
    device_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    enrolment_id  UUID UNIQUE NOT NULL REFERENCES enrolment(enrolment_id) ON DELETE RESTRICT,
    name          VARCHAR(80)  NOT NULL,
    imei          VARCHAR(15)  UNIQUE NOT NULL,
    imei_two      VARCHAR(15)  NOT NULL,
    serial_number VARCHAR(20)  NOT NULL,
    model         VARCHAR(40)  NOT NULL,
    brand         VARCHAR(40)  NOT NULL,
    product_name  VARCHAR(40)  NOT NULL,
    state         device_state NOT NULL DEFAULT 'Active',
    created_at    TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_device_enrolment ON device(enrolment_id);

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

-- sim
CREATE TABLE IF NOT EXISTS sim (
    sim_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id  UUID NOT NULL REFERENCES device(device_id) ON DELETE CASCADE,
    icc_id     VARCHAR(30) UNIQUE NOT NULL,
    slot_index VARCHAR(10) NOT NULL,
    operator   VARCHAR(50) NOT NULL,
    number     VARCHAR(20) NOT NULL,
    state      VARCHAR(20) NOT NULL DEFAULT 'Active',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_sim_device ON sim(device_id);

-- plan
CREATE TABLE plan (
    plan_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id        UUID NOT NULL REFERENCES "user"(user_id) ON DELETE RESTRICT,
    vendor_id      UUID NOT NULL REFERENCES "user"(user_id) ON DELETE RESTRICT,
    device_id      UUID REFERENCES device(device_id) ON DELETE RESTRICT,
    television_id  UUID REFERENCES television(television_id) ON DELETE RESTRICT,
    initial_date   DATE NOT NULL,
    quotas         SMALLINT NOT NULL,
    period         INT,
    value          NUMERIC(10,2) NOT NULL,
    contract       VARCHAR(80) NOT NULL,
    CONSTRAINT chk_plan_device_or_tv CHECK (
        (device_id IS NOT NULL)::int + (television_id IS NOT NULL)::int = 1
    )
);
CREATE INDEX IF NOT EXISTS idx_plan_device ON plan(device_id);
CREATE INDEX IF NOT EXISTS idx_plan_television ON plan(television_id);

-- payment
CREATE TABLE IF NOT EXISTS payment (
    payment_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id      UUID REFERENCES device(device_id) ON DELETE RESTRICT,
    television_id  UUID REFERENCES television(television_id) ON DELETE RESTRICT,
    plan_id        UUID NOT NULL REFERENCES plan(plan_id) ON DELETE CASCADE,
    value          NUMERIC(10,2) NOT NULL,
    method         VARCHAR(20)   NOT NULL,
    state          payment_state NOT NULL,
    date           TIMESTAMPTZ   NOT NULL,
    reference      VARCHAR(80)   NOT NULL,
    CONSTRAINT chk_payment_device_or_tv CHECK (
        ((device_id IS NOT NULL)::int + (television_id IS NOT NULL)::int) = 1
    )
);
CREATE INDEX IF NOT EXISTS idx_payment_plan ON payment(plan_id);
CREATE INDEX IF NOT EXISTS idx_payment_device ON payment(device_id);
CREATE INDEX IF NOT EXISTS idx_payment_television ON payment(television_id);

-- action (PK y FKs siguiendo convención Tortoise: *_id)
CREATE TABLE IF NOT EXISTS action (
    action_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id   UUID NOT NULL,
    applied_by_id UUID NOT NULL,
    state       action_state NOT NULL DEFAULT 'pending',
    action      action_type  NOT NULL,
    description VARCHAR(255),
    created_at  TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- FKs action (idempotentes)
DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu ON tc.constraint_name=kcu.constraint_name
        WHERE tc.table_name='action' AND tc.constraint_type='FOREIGN KEY' AND kcu.column_name='device_id'
    ) THEN
        ALTER TABLE action
        ADD CONSTRAINT fk_action_device
        FOREIGN KEY (device_id) REFERENCES device(device_id) ON DELETE CASCADE;
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu ON tc.constraint_name=kcu.constraint_name
        WHERE tc.table_name='action' AND tc.constraint_type='FOREIGN KEY' AND kcu.column_name='applied_by_id'
    ) THEN
        ALTER TABLE action
        ADD CONSTRAINT fk_action_applied_by
        FOREIGN KEY (applied_by_id) REFERENCES "user"(user_id) ON DELETE RESTRICT;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_action_device ON action(device_id);
CREATE INDEX IF NOT EXISTS idx_action_applied_by_id ON action(applied_by_id);

-- location
CREATE TABLE IF NOT EXISTS location (
    location_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id   UUID NOT NULL REFERENCES device(device_id) ON DELETE CASCADE,
    latitude    DOUBLE PRECISION NOT NULL,
    longitude   DOUBLE PRECISION NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_location_device ON location(device_id);
CREATE INDEX IF NOT EXISTS idx_location_device ON location(device_id);

-- factory reset protection (FRP)
CREATE TABLE IF NOT EXISTS "factoryResetProtection" (
    factory_reset_protection_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id  VARCHAR(40) NOT NULL,
    name        VARCHAR(255) NOT NULL,
    email       VARCHAR(80)  NOT NULL,
    state       frp_state NOT NULL DEFAULT 'Active',
    store_id    UUID,
    CONSTRAINT uq_frp_account_store UNIQUE (account_id, store_id),
    CONSTRAINT uq_frp_email_store   UNIQUE (email, store_id)
);

-- FK opcional para FRP → store
DO $$ BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='store')
       AND NOT EXISTS (
         SELECT 1 FROM information_schema.table_constraints
         WHERE table_name='factoryResetProtection' AND constraint_type='FOREIGN KEY'
       ) THEN
        ALTER TABLE "factoryResetProtection"
        ADD CONSTRAINT fk_frp_store
        FOREIGN KEY (store_id) REFERENCES store(id) ON DELETE CASCADE;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_frp_store ON "factoryResetProtection"(store_id);

-- authentication (según Pydantic)
CREATE TABLE IF NOT EXISTS authentication (
    authentication_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username   VARCHAR(50)  NOT NULL UNIQUE,
    password   VARCHAR(255) NOT NULL,
    email      VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_auth_username ON authentication(username);
CREATE INDEX IF NOT EXISTS idx_auth_email    ON authentication(email);

-- group (si tu repo incluye models/group.py)
CREATE TABLE IF NOT EXISTS "group" (
    group_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name     VARCHAR(80) NOT NULL,
    state    VARCHAR(10) NOT NULL DEFAULT 'Active'
);

-- device_group (relación many-to-many)
CREATE TABLE IF NOT EXISTS device_group (
    id        BIGSERIAL PRIMARY KEY,
    device_id UUID NOT NULL REFERENCES device(device_id) ON DELETE CASCADE,
    group_id  UUID NOT NULL REFERENCES "group"(group_id) ON DELETE CASCADE,
    CONSTRAINT uq_device_group UNIQUE (device_id, group_id)
);

-- =======================
--  COMPAT: reparar esquemas antiguos
-- =======================

-- (A) action: si existía PK "id", migrarla a action_id
DO $$ DECLARE
    has_id bool;
    has_action_id bool;
BEGIN
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='action' AND column_name='id'
    ) INTO has_id;

    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='action' AND column_name='action_id'
    ) INTO has_action_id;

    IF has_id AND has_action_id THEN
        -- Copiar valores si action_id está NULL
        EXECUTE 'UPDATE action SET action_id = id WHERE action_id IS NULL';
        -- Cambiar PK a action_id si la PK actual es sobre "id"
        IF EXISTS (
            SELECT 1 FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu ON tc.constraint_name=kcu.constraint_name
            WHERE tc.table_name='action' AND tc.constraint_type='PRIMARY KEY' AND kcu.column_name='id'
        ) THEN
            EXECUTE (
                SELECT format('ALTER TABLE action DROP CONSTRAINT %I', tc.constraint_name)
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu ON tc.constraint_name=kcu.constraint_name
                WHERE tc.table_name='action' AND tc.constraint_type='PRIMARY KEY' AND kcu.column_name='id'
                LIMIT 1
            );
            ALTER TABLE action ADD CONSTRAINT pk_action PRIMARY KEY (action_id);
            ALTER TABLE action DROP COLUMN id;
        END IF;
    ELSIF has_id AND NOT has_action_id THEN
        -- Crear action_id, copiar y setear PK
        ALTER TABLE action ADD COLUMN action_id UUID;
        EXECUTE 'UPDATE action SET action_id = id';
        EXECUTE 'UPDATE action SET action_id = gen_random_uuid() WHERE action_id IS NULL';
        -- Dropear PK vieja si estaba en "id"
        IF EXISTS (
            SELECT 1 FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu ON tc.constraint_name=kcu.constraint_name
            WHERE tc.table_name='action' AND tc.constraint_type='PRIMARY KEY' AND kcu.column_name='id'
        ) THEN
            EXECUTE (
                SELECT format('ALTER TABLE action DROP CONSTRAINT %I', tc.constraint_name)
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu ON tc.constraint_name=kcu.constraint_name
                WHERE tc.table_name='action' AND tc.constraint_type='PRIMARY KEY' AND kcu.column_name='id'
                LIMIT 1
            );
        END IF;
        ALTER TABLE action ADD CONSTRAINT pk_action PRIMARY KEY (action_id);
        ALTER TABLE action DROP COLUMN id;
    ELSE
        -- nada que hacer
        NULL;
    END IF;
END $$;

-- (B) action: si existía "applied_by" sin sufijo _id, migrarla a applied_by_id
DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='action' AND column_name='applied_by_id'
    ) THEN
        ALTER TABLE action ADD COLUMN applied_by_id UUID;
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='action' AND column_name='applied_by'
    ) THEN
        UPDATE action SET applied_by_id = applied_by WHERE applied_by_id IS NULL;
        ALTER TABLE action DROP COLUMN applied_by;
    END IF;

    -- Crear FK si falta
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu ON tc.constraint_name=kcu.constraint_name
        WHERE tc.table_name='action' AND tc.constraint_type='FOREIGN KEY' AND kcu.column_name='applied_by_id'
    ) THEN
        ALTER TABLE action
        ADD CONSTRAINT fk_action_applied_by
        FOREIGN KEY (applied_by_id) REFERENCES "user"(user_id) ON DELETE RESTRICT;
    END IF;
END $$;

-- (C) ÍNDICE viejo sobre applied_by: eliminarlo si existía y recrear el nuevo
DO $$ BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE schemaname='public' AND indexname='idx_action_applied_by'
    ) THEN
        DROP INDEX idx_action_applied_by;
    END IF;
END $$;
CREATE INDEX IF NOT EXISTS idx_action_applied_by_id ON action(applied_by_id);

-- =======================
--  Resolver circularidad: admin_id en store → FK a user
-- =======================
DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='store' AND column_name='admin_id'
    ) THEN
        ALTER TABLE store ADD COLUMN admin_id UUID NULL;
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu ON tc.constraint_name=kcu.constraint_name
        WHERE tc.table_name='store' AND tc.constraint_type='FOREIGN KEY' AND kcu.column_name='admin_id'
    ) THEN
        ALTER TABLE store
        ADD CONSTRAINT fk_store_admin
        FOREIGN KEY (admin_id) REFERENCES "user"(user_id) ON DELETE SET NULL;
    END IF;
END $$;

-- =======================
--  Fin
-- =======================
