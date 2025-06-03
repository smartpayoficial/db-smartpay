-- Create the database if it doesn't exist
CREATE DATABASE smartpay_test_db;

-- Connect to the database
\c smartpay_test_db;

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
    key VARCHAR(50) UNIQUE NOT NULL,
    value VARCHAR(255) NOT NULL,
    description VARCHAR(255) NOT NULL
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
    enrolment_id UUID NOT NULL REFERENCES "enrolment"(enrolment_id),
    name VARCHAR(80) NOT NULL,
    imei VARCHAR(15) NOT NULL,
    imei_two VARCHAR(15) NOT NULL,
    serial_number VARCHAR(20) NOT NULL,
    model VARCHAR(40) NOT NULL,
    brand VARCHAR(40) NOT NULL,
    product_name VARCHAR(40) NOT NULL,
    state device_state NOT NULL DEFAULT 'Active'
);
