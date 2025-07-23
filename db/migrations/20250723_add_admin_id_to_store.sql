-- +goose Up
-- SQL in this section is executed when the migration is applied
ALTER TABLE store
ADD COLUMN admin_id UUID REFERENCES "user"(id);

-- +goose Down
-- SQL in this section is executed when the migration is rolled back
ALTER TABLE store
DROP COLUMN admin_id;
