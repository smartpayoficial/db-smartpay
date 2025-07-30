-- Increase the maximum length of the value field in the configuration table
ALTER TABLE configuration ALTER COLUMN value TYPE VARCHAR(1000);
