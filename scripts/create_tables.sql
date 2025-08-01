-- Script para crear las tablas de la base de datos smartpay
-- Este script crea las tablas en un orden específico para evitar problemas de referencias circulares

-- Tablas sin dependencias (nivel 1)
CREATE TABLE IF NOT EXISTS "role" (
    "role_id" UUID PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL,
    "description" VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS "country" (
    "country_id" UUID PRIMARY KEY,
    "name" VARCHAR(100) NOT NULL,
    "code" VARCHAR(10) NOT NULL
);

-- Tablas con dependencias simples (nivel 2)
CREATE TABLE IF NOT EXISTS "region" (
    "region_id" UUID PRIMARY KEY,
    "name" VARCHAR(100) NOT NULL,
    "country_id" UUID NOT NULL REFERENCES "country" ("country_id") ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "store" (
    "id" UUID PRIMARY KEY,
    "nombre" VARCHAR(100) NOT NULL,
    "country_id" UUID REFERENCES "country" ("country_id"),
    "tokens_disponibles" INTEGER DEFAULT 0,
    "plan" VARCHAR(50),
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "back_link" VARCHAR(255),
    "db_link" VARCHAR(255),
    "admin_id" UUID NULL
);

-- Tablas con dependencias de nivel 2 (nivel 3)
CREATE TABLE IF NOT EXISTS "city" (
    "city_id" UUID PRIMARY KEY,
    "name" VARCHAR(100) NOT NULL,
    "region_id" UUID NOT NULL REFERENCES "region" ("region_id") ON DELETE CASCADE
);

-- Tablas con dependencias de nivel 3 (nivel 4)
CREATE TABLE IF NOT EXISTS "user" (
    "user_id" UUID PRIMARY KEY,
    "username" VARCHAR(50) NOT NULL,
    "password" VARCHAR(255) NOT NULL,
    "email" VARCHAR(100) NOT NULL,
    "first_name" VARCHAR(50) NOT NULL,
    "middle_name" VARCHAR(50),
    "last_name" VARCHAR(50) NOT NULL,
    "second_last_name" VARCHAR(50),
    "dni" VARCHAR(20) NOT NULL,
    "phone" VARCHAR(20),
    "address" VARCHAR(255),
    "prefix" VARCHAR(10),
    "state" VARCHAR(20) NOT NULL,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "role_id" UUID REFERENCES "role" ("role_id"),
    "city_id" UUID REFERENCES "city" ("city_id"),
    "store_id" UUID REFERENCES "store" ("id")
);

-- Actualizar la referencia circular en store después de crear la tabla user
ALTER TABLE "store" ADD CONSTRAINT "fk_store_admin" FOREIGN KEY ("admin_id") REFERENCES "user" ("user_id");

CREATE TABLE IF NOT EXISTS "device" (
    "device_id" UUID PRIMARY KEY,
    "name" VARCHAR(100) NOT NULL,
    "imei" VARCHAR(50) NOT NULL,
    "brand" VARCHAR(50),
    "model" VARCHAR(50),
    "state" VARCHAR(20) NOT NULL,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS "group" (
    "group_id" UUID PRIMARY KEY,
    "name" VARCHAR(100) NOT NULL,
    "description" VARCHAR(255),
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "user_id" UUID REFERENCES "user" ("user_id")
);

-- Tablas con dependencias de nivel 4 (nivel 5)
CREATE TABLE IF NOT EXISTS "action" (
    "action_id" UUID PRIMARY KEY,
    "action" VARCHAR(50) NOT NULL,
    "description" VARCHAR(255),
    "state" VARCHAR(20) NOT NULL,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "device_id" UUID REFERENCES "device" ("device_id"),
    "applied_by_id" UUID REFERENCES "user" ("user_id")
);

CREATE TABLE IF NOT EXISTS "enrolment" (
    "enrolment_id" UUID PRIMARY KEY,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "user_id" UUID REFERENCES "user" ("user_id"),
    "device_id" UUID REFERENCES "device" ("device_id")
);

CREATE TABLE IF NOT EXISTS "location" (
    "location_id" UUID PRIMARY KEY,
    "latitude" DECIMAL(10, 8) NOT NULL,
    "longitude" DECIMAL(11, 8) NOT NULL,
    "altitude" DECIMAL(10, 2),
    "accuracy" DECIMAL(10, 2),
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "device_id" UUID REFERENCES "device" ("device_id")
);

CREATE TABLE IF NOT EXISTS "sim" (
    "sim_id" UUID PRIMARY KEY,
    "iccid" VARCHAR(50) NOT NULL,
    "phone_number" VARCHAR(20),
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "device_id" UUID REFERENCES "device" ("device_id")
);

CREATE TABLE IF NOT EXISTS "payment" (
    "payment_id" UUID PRIMARY KEY,
    "reference" VARCHAR(100) NOT NULL,
    "value" DECIMAL(10, 2) NOT NULL,
    "method" VARCHAR(50) NOT NULL,
    "state" VARCHAR(20) NOT NULL,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "user_id" UUID REFERENCES "user" ("user_id"),
    "vendor_id" UUID REFERENCES "user" ("user_id")
);

CREATE TABLE IF NOT EXISTS "authentication" (
    "authentication_id" UUID PRIMARY KEY,
    "token" VARCHAR(255) NOT NULL,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "user_id" UUID REFERENCES "user" ("user_id")
);

CREATE TABLE IF NOT EXISTS "configuration" (
    "configuration_id" UUID PRIMARY KEY,
    "key" VARCHAR(100) NOT NULL,
    "value" VARCHAR(255) NOT NULL,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "device_id" UUID REFERENCES "device" ("device_id")
);

CREATE TABLE IF NOT EXISTS "factory_reset_protection" (
    "factory_reset_protection_id" UUID PRIMARY KEY,
    "state" VARCHAR(20) NOT NULL,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "device_id" UUID REFERENCES "device" ("device_id"),
    "user_id" UUID REFERENCES "user" ("user_id")
);

-- Tablas de relaciones muchos a muchos
CREATE TABLE IF NOT EXISTS "user_group" (
    "user_id" UUID REFERENCES "user" ("user_id"),
    "group_id" UUID REFERENCES "group" ("group_id"),
    PRIMARY KEY ("user_id", "group_id")
);

CREATE TABLE IF NOT EXISTS "device_group" (
    "device_id" UUID REFERENCES "device" ("device_id"),
    "group_id" UUID REFERENCES "group" ("group_id"),
    PRIMARY KEY ("device_id", "group_id")
);
