-- Migración para agregar admin_id a la tabla store

ALTER TABLE store ADD COLUMN admin_id UUID REFERENCES "user"(user_id);

COMMENT ON COLUMN store.admin_id IS 'Usuario administrador de la tienda';
