-- Migración para agregar store_id a la tabla user

ALTER TABLE "user" ADD COLUMN store_id UUID REFERENCES store(id);

COMMENT ON COLUMN "user".store_id IS 'Tienda a la que pertenece el usuario';
