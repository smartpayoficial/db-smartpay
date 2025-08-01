-- Script SQL para corregir problemas de zonas horarias en PostgreSQL
-- Este script configura la base de datos para usar UTC de manera consistente

-- Configurar la zona horaria de la sesión a UTC
SET timezone = 'UTC';

-- Actualizar la configuración de PostgreSQL para manejar fechas sin zona horaria
ALTER DATABASE CURRENT_SET timezone = 'UTC';

-- Actualizar la configuración de PostgreSQL para que todas las nuevas conexiones usen UTC
ALTER DATABASE CURRENT_SET timezone TO 'UTC';

-- Mostrar la configuración actual para verificar
SHOW timezone;
