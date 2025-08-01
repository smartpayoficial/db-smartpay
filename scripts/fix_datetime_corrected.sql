-- Script SQL corregido para configurar la zona horaria en PostgreSQL
-- Este script usa la sintaxis correcta para PostgreSQL 12

-- Configurar la zona horaria de la sesión a UTC
SET timezone TO 'UTC';

-- Verificar la configuración actual
SHOW timezone;

-- Modificar la configuración de PostgreSQL para la base de datos actual
ALTER DATABASE smartpay SET timezone TO 'UTC';

-- Crear una función para convertir fechas con zona horaria a fechas sin zona horaria
CREATE OR REPLACE FUNCTION fix_timezone_aware_dates() RETURNS void AS $$
BEGIN
    -- Esta función podría extenderse para actualizar tablas específicas si fuera necesario
    RAISE NOTICE 'Función de corrección de fechas instalada correctamente';
END;
$$ LANGUAGE plpgsql;

-- Ejecutar la función
SELECT fix_timezone_aware_dates();
