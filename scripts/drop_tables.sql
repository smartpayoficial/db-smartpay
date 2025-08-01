-- Script para eliminar todas las tablas de la base de datos
DO $$ 
DECLARE
    r RECORD;
BEGIN
    -- Desactivar restricciones de clave foránea temporalmente
    EXECUTE 'SET CONSTRAINTS ALL DEFERRED';
    
    -- Eliminar todas las tablas en el esquema public
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
        EXECUTE 'DROP TABLE IF EXISTS "' || r.tablename || '" CASCADE';
    END LOOP;
    
    RAISE NOTICE 'Todas las tablas han sido eliminadas.';
END $$;
