-- Create the database if it doesn't exist
CREATE DATABASE smartpay_test_db;

-- Connect to the database
\c smartpay_test_db;

-- Enable pgcrypto extension for gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Create enum types
CREATE TYPE user_state AS ENUM ('Active', 'Inactive');
CREATE TYPE device_state AS ENUM ('Active', 'Inactive');

-- Create country table
CREATE TABLE IF NOT EXISTS "country" (
    country_id UUID PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(3) NOT NULL
);

-- Create region table
CREATE TABLE IF NOT EXISTS "region" (
    region_id UUID PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    country_id UUID NOT NULL REFERENCES "country"(country_id)
);

-- Create city table
CREATE TABLE IF NOT EXISTS "city" (
    city_id UUID PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    region_id UUID NOT NULL REFERENCES "region"(region_id)
);

-- Create role table
CREATE TABLE IF NOT EXISTS "role" (
    role_id UUID PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description VARCHAR(255) NOT NULL
);

-- Create configuration table
CREATE TABLE IF NOT EXISTS "configuration" (
    configuration_id UUID PRIMARY KEY,
    key VARCHAR(50) NOT NULL,
    value VARCHAR(1000) NOT NULL,
    description VARCHAR(255) NOT NULL,
    store_id UUID,
    UNIQUE(key, store_id),
    FOREIGN KEY (store_id) REFERENCES store(id)
);

-- Create authentication table
CREATE TABLE IF NOT EXISTS "authentication" (
    authentication_id UUID PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL
);

-- Create user table with all attributes
CREATE TABLE IF NOT EXISTS "user" (
    user_id UUID PRIMARY KEY,
    city_id UUID NOT NULL REFERENCES "city"(city_id),
    dni VARCHAR(16) UNIQUE NOT NULL,
    first_name VARCHAR(40) NOT NULL,
    middle_name VARCHAR(40),
    last_name VARCHAR(40) NOT NULL,
    second_last_name VARCHAR(40),
    email VARCHAR(80) NOT NULL,
    prefix VARCHAR(4) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    address VARCHAR(255) NOT NULL,
    state user_state NOT NULL DEFAULT 'Active',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create enrolment table
CREATE TABLE IF NOT EXISTS "enrolment" (
    enrolment_id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES "user"(user_id),
    vendor_id UUID NOT NULL REFERENCES "user"(user_id),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create device table
CREATE TABLE IF NOT EXISTS "device" (
    device_id UUID PRIMARY KEY,
    enrolment_id UUID NOT NULL UNIQUE REFERENCES "enrolment"(enrolment_id),
    name VARCHAR(80) NOT NULL,
    imei VARCHAR(15) NOT NULL UNIQUE,
    imei_two VARCHAR(15) NOT NULL UNIQUE,
    serial_number VARCHAR(20) NOT NULL,
    model VARCHAR(40) NOT NULL,
    brand VARCHAR(40) NOT NULL,
    product_name VARCHAR(40) NOT NULL,
    state device_state NOT NULL DEFAULT 'Active'
);

-- Create sim table
CREATE TABLE IF NOT EXISTS "sim" (
    sim_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id UUID NOT NULL REFERENCES "device"(device_id),
    icc_id VARCHAR(30) NOT NULL,
    slot_index VARCHAR(10) NOT NULL,
    operator VARCHAR(50) NOT NULL,
    number VARCHAR(20) NOT NULL,
    state VARCHAR(20) NOT NULL DEFAULT 'Active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_sim_number UNIQUE (number),
    CONSTRAINT uq_sim_icc_id UNIQUE (icc_id)
);

CREATE INDEX idx_sim_device_id ON "sim"(device_id);

-- Create factory reset protection table
CREATE TABLE IF NOT EXISTS "factoryResetProtection" (
    factory_reset_protection_id UUID PRIMARY KEY,
    account_id VARCHAR(40) NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(80) NOT NULL,
    state VARCHAR(20) NOT NULL DEFAULT 'Active',
    store_id UUID,
    FOREIGN KEY (store_id) REFERENCES store(id),
    UNIQUE(account_id, store_id),
    UNIQUE(email, store_id)
);
