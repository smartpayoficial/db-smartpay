-- Set search path to your schema if needed, e.g., SET search_path TO your_schema_name;

-- Insert Countries
INSERT INTO country (country_id, name, code, phone_code, flag_icon_url) VALUES
(uuid_generate_v4(), 'Argentina', 'AR', '+54', 'https://upload.wikimedia.org/wikipedia/commons/1/1a/Flag_of_Argentina.svg'),
(uuid_generate_v4(), 'Bolivia', 'BO', '+591', 'https://upload.wikimedia.org/wikipedia/commons/4/48/Flag_of_Bolivia.svg'),
(uuid_generate_v4(), 'Brazil', 'BR', '+55', 'https://upload.wikimedia.org/wikipedia/commons/0/05/Flag_of_Brazil.svg'),
(uuid_generate_v4(), 'Chile', 'CL', '+56', 'https://upload.wikimedia.org/wikipedia/commons/7/78/Flag_of_Chile.svg'),
(uuid_generate_v4(), 'Colombia', 'CO', '+57', 'https://upload.wikimedia.org/wikipedia/commons/2/21/Flag_of_Colombia.svg'),
(uuid_generate_v4(), 'Costa Rica', 'CR', '+506', 'https://upload.wikimedia.org/wikipedia/commons/f/f2/Flag_of_Costa_Rica.svg'),
(uuid_generate_v4(), 'Cuba', 'CU', '+53', 'https://upload.wikimedia.org/wikipedia/commons/b/bd/Flag_of_Cuba.svg'),
(uuid_generate_v4(), 'Dominican Republic', 'DO', '+1-809', 'https://upload.wikimedia.org/wikipedia/commons/9/9f/Flag_of_the_Dominican_Republic.svg'),
(uuid_generate_v4(), 'Ecuador', 'EC', '+593', 'https://upload.wikimedia.org/wikipedia/commons/e/e8/Flag_of_Ecuador.svg'),
(uuid_generate_v4(), 'El Salvador', 'SV', '+503', 'https://upload.wikimedia.org/wikipedia/commons/3/34/Flag_of_El_Salvador.svg'),
(uuid_generate_v4(), 'Guatemala', 'GT', '+502', 'https://upload.wikimedia.org/wikipedia/commons/e/ec/Flag_of_Guatemala.svg'),
(uuid_generate_v4(), 'Honduras', 'HN', '+504', 'https://upload.wikimedia.org/wikipedia/commons/8/82/Flag_of_Honduras_%282022%E2%80%93present%29.svg'),
(uuid_generate_v4(), 'Mexico', 'MX', '+52', 'https://upload.wikimedia.org/wikipedia/commons/f/fc/Flag_of_Mexico.svg'),
(uuid_generate_v4(), 'Nicaragua', 'NI', '+505', 'https://upload.wikimedia.org/wikipedia/commons/1/19/Flag_of_Nicaragua.svg'),
(uuid_generate_v4(), 'Panama', 'PA', '+507', 'https://upload.wikimedia.org/wikipedia/commons/a/ab/Flag_of_Panama.svg'),
(uuid_generate_v4(), 'Paraguay', 'PY', '+595', 'https://upload.wikimedia.org/wikipedia/commons/2/27/Flag_of_Paraguay.svg'),
(uuid_generate_v4(), 'Peru', 'PE', '+51', 'https://upload.wikimedia.org/wikipedia/commons/c/cf/Flag_of_Peru.svg'),
(uuid_generate_v4(), 'Uruguay', 'UY', '+598', 'https://upload.wikimedia.org/wikipedia/commons/f/fe/Flag_of_Uruguay.svg'),
(uuid_generate_v4(), 'Venezuela', 'VE', '+58', 'https://upload.wikimedia.org/wikipedia/commons/0/06/Flag_of_Venezuela.svg');

-- Declare UUID variables for countries
DO $$
DECLARE
    arg_id UUID;
    bol_id UUID;
    bra_id UUID;
    chi_id UUID;
    col_id UUID;
    cri_id UUID;
    cub_id UUID;
    dom_id UUID;
    ecu_id UUID;
    els_id UUID;
    gua_id UUID;
    hon_id UUID;
    mex_id UUID;
    nic_id UUID;
    pan_id UUID;
    par_id UUID;
    per_id UUID;
    uru_id UUID;
    ven_id UUID;

    -- Declare UUID variables for regions (will be assigned in respective blocks)
    bogota_region_id UUID;
    antioquia_region_id UUID;
    valle_region_id UUID;
    cundinamarca_region_id UUID;
    jalisco_region_id UUID;
    mexico_state_region_id UUID;
    buenos_aires_region_id UUID;
    sao_paulo_region_id UUID;
    rio_janeiro_region_id UUID;

BEGIN
    -- Get Country IDs
    SELECT country_id INTO arg_id FROM country WHERE code = 'AR';
    SELECT country_id INTO bol_id FROM country WHERE code = 'BO';
    SELECT country_id INTO bra_id FROM country WHERE code = 'BR';
    SELECT country_id INTO chi_id FROM country WHERE code = 'CL';
    SELECT country_id INTO col_id FROM country WHERE code = 'CO';
    SELECT country_id INTO cri_id FROM country WHERE code = 'CR';
    SELECT country_id INTO cub_id FROM country WHERE code = 'CU';
    SELECT country_id INTO dom_id FROM country WHERE code = 'DO';
    SELECT country_id INTO ecu_id FROM country WHERE code = 'EC';
    SELECT country_id INTO els_id FROM country WHERE code = 'SV';
    SELECT country_id INTO gua_id FROM country WHERE code = 'GT';
    SELECT country_id INTO hon_id FROM country WHERE code = 'HN';
    SELECT country_id INTO mex_id FROM country WHERE code = 'MX';
    SELECT country_id INTO nic_id FROM country WHERE code = 'NI';
    SELECT country_id INTO pan_id FROM country WHERE code = 'PA';
    SELECT country_id INTO par_id FROM country WHERE code = 'PY';
    SELECT country_id INTO per_id FROM country WHERE code = 'PE';
    SELECT country_id INTO uru_id FROM country WHERE code = 'UY';
    SELECT country_id INTO ven_id FROM country WHERE code = 'VE';

    -- Insert Regions for Colombia
    INSERT INTO region (region_id, name, country_id) VALUES
    (uuid_generate_v4(), 'Bogotá D.C.', col_id) RETURNING region_id INTO bogota_region_id;
    INSERT INTO region (region_id, name, country_id) VALUES
    (uuid_generate_v4(), 'Antioquia', col_id) RETURNING region_id INTO antioquia_region_id;
    INSERT INTO region (region_id, name, country_id) VALUES
    (uuid_generate_v4(), 'Valle del Cauca', col_id) RETURNING region_id INTO valle_region_id;
    INSERT INTO region (region_id, name, country_id) VALUES
    (uuid_generate_v4(), 'Cundinamarca', col_id) RETURNING region_id INTO cundinamarca_region_id;
    INSERT INTO region (region_id, name, country_id) VALUES
    (uuid_generate_v4(), 'Atlántico', col_id);
    INSERT INTO region (region_id, name, country_id) VALUES
    (uuid_generate_v4(), 'Santander', col_id);
    INSERT INTO region (region_id, name, country_id) VALUES
    (uuid_generate_v4(), 'Bolívar', col_id);

    -- Insert Cities for Colombia (Examples)
    INSERT INTO city (city_id, name, region_id) VALUES
    (uuid_generate_v4(), 'Bogotá', bogota_region_id);
    INSERT INTO city (city_id, name, region_id) VALUES
    (uuid_generate_v4(), 'Medellín', antioquia_region_id),
    (uuid_generate_v4(), 'Envigado', antioquia_region_id),
    (uuid_generate_v4(), 'Itagüí', antioquia_region_id);
    INSERT INTO city (city_id, name, region_id) VALUES
    (uuid_generate_v4(), 'Cali', valle_region_id),
    (uuid_generate_v4(), 'Palmira', valle_region_id),
    (uuid_generate_v4(), 'Buga', valle_region_id);
    INSERT INTO city (city_id, name, region_id) VALUES
    (uuid_generate_v4(), 'Soacha', cundinamarca_region_id),
    (uuid_generate_v4(), 'Zipaquirá', cundinamarca_region_id),
    (uuid_generate_v4(), 'Chía', cundinamarca_region_id);

    -- Insert Regions for Mexico
    INSERT INTO region (region_id, name, country_id) VALUES
    (uuid_generate_v4(), 'Jalisco', mex_id) RETURNING region_id INTO jalisco_region_id;
    INSERT INTO region (region_id, name, country_id) VALUES
    (uuid_generate_v4(), 'Ciudad de México', mex_id);
    INSERT INTO region (region_id, name, country_id) VALUES
    (uuid_generate_v4(), 'Estado de México', mex_id) RETURNING region_id INTO mexico_state_region_id;
    INSERT INTO region (region_id, name, country_id) VALUES
    (uuid_generate_v4(), 'Nuevo León', mex_id);
    INSERT INTO region (region_id, name, country_id) VALUES
    (uuid_generate_v4(), 'Veracruz', mex_id);
    INSERT INTO region (region_id, name, country_id) VALUES
    (uuid_generate_v4(), 'Puebla', mex_id);

    -- Insert Cities for Mexico (Examples)
    INSERT INTO city (city_id, name, region_id) VALUES
    (uuid_generate_v4(), 'Guadalajara', jalisco_region_id),
    (uuid_generate_v4(), 'Zapopan', jalisco_region_id),
    (uuid_generate_v4(), 'Tlaquepaque', jalisco_region_id);
    INSERT INTO city (city_id, name, region_id) VALUES
    (uuid_generate_v4(), 'Naucalpan de Juárez', mexico_state_region_id),
    (uuid_generate_v4(), 'Ecatepec de Morelos', mexico_state_region_id),
    (uuid_generate_v4(), 'Nezahualcóyotl', mexico_state_region_id);

    -- Insert Regions for Argentina
    INSERT INTO region (region_id, name, country_id) VALUES
    (uuid_generate_v4(), 'Buenos Aires (Provincia)', arg_id) RETURNING region_id INTO buenos_aires_region_id;
    INSERT INTO region (region_id, name, country_id) VALUES
    (uuid_generate_v4(), 'Ciudad Autónoma de Buenos Aires', arg_id);
    INSERT INTO region (region_id, name, country_id) VALUES
    (uuid_generate_v4(), 'Córdoba', arg_id);
    INSERT INTO region (region_id, name, country_id) VALUES
    (uuid_generate_v4(), 'Santa Fe', arg_id);

    -- Insert Cities for Argentina (Examples)
    INSERT INTO city (city_id, name, region_id) VALUES
    (uuid_generate_v4(), 'La Plata', buenos_aires_region_id),
    (uuid_generate_v4(), 'Mar del Plata', buenos_aires_region_id),
    (uuid_generate_v4(), 'Bahía Blanca', buenos_aires_region_id);

    -- Insert Regions for Brazil
    INSERT INTO region (region_id, name, country_id) VALUES
    (uuid_generate_v4(), 'São Paulo', bra_id) RETURNING region_id INTO sao_paulo_region_id;
    INSERT INTO region (region_id, name, country_id) VALUES
    (uuid_generate_v4(), 'Rio de Janeiro', bra_id) RETURNING region_id INTO rio_janeiro_region_id;
    INSERT INTO region (region_id, name, country_id) VALUES
    (uuid_generate_v4(), 'Minas Gerais', bra_id);
    INSERT INTO region (region_id, name, country_id) VALUES
    (uuid_generate_v4(), 'Bahia', bra_id);

    -- Insert Cities for Brazil (Examples)
    INSERT INTO city (city_id, name, region_id) VALUES
    (uuid_generate_v4(), 'São Paulo', sao_paulo_region_id),
    (uuid_generate_v4(), 'Guarulhos', sao_paulo_region_id),
    (uuid_generate_v4(), 'Campinas', sao_paulo_region_id);
    INSERT INTO city (city_id, name, region_id) VALUES
    (uuid_generate_v4(), 'Rio de Janeiro', rio_janeiro_region_id),
    (uuid_generate_v4(), 'Niterói', rio_janeiro_region_id),
    (uuid_generate_v4(), 'Duque de Caxias', rio_janeiro_region_id);

    -- Insert Regions and some cities for other countries (abbreviated for brevity)

    -- Chile
    INSERT INTO region (region_id, name, country_id) VALUES (uuid_generate_v4(), 'Región Metropolitana de Santiago', chi_id) RETURNING region_id INTO bogota_region_id; -- Reusing variable name
    INSERT INTO city (city_id, name, region_id) VALUES (uuid_generate_v4(), 'Santiago', bogota_region_id), (uuid_generate_v4(), 'Puente Alto', bogota_region_id);
    INSERT INTO region (region_id, name, country_id) VALUES (uuid_generate_v4(), 'Valparaíso', chi_id) RETURNING region_id INTO bogota_region_id;
    INSERT INTO city (city_id, name, region_id) VALUES (uuid_generate_v4(), 'Valparaíso', bogota_region_id), (uuid_generate_v4(), 'Viña del Mar', bogota_region_id);

    -- Peru
    INSERT INTO region (region_id, name, country_id) VALUES (uuid_generate_v4(), 'Lima', per_id) RETURNING region_id INTO bogota_region_id;
    INSERT INTO city (city_id, name, region_id) VALUES (uuid_generate_v4(), 'Lima', bogota_region_id), (uuid_generate_v4(), 'Callao', bogota_region_id);
    INSERT INTO region (region_id, name, country_id) VALUES (uuid_generate_v4(), 'Cusco', per_id) RETURNING region_id INTO bogota_region_id;
    INSERT INTO city (city_id, name, region_id) VALUES (uuid_generate_v4(), 'Cusco', bogota_region_id);

    -- Ecuador
    INSERT INTO region (region_id, name, country_id) VALUES (uuid_generate_v4(), 'Pichincha', ecu_id) RETURNING region_id INTO bogota_region_id;
    INSERT INTO city (city_id, name, region_id) VALUES (uuid_generate_v4(), 'Quito', bogota_region_id);
    INSERT INTO region (region_id, name, country_id) VALUES (uuid_generate_v4(), 'Guayas', ecu_id) RETURNING region_id INTO bogota_region_id;
    INSERT INTO city (city_id, name, region_id) VALUES (uuid_generate_v4(), 'Guayaquil', bogota_region_id);

    -- Bolivia
    INSERT INTO region (region_id, name, country_id) VALUES (uuid_generate_v4(), 'La Paz', bol_id) RETURNING region_id INTO bogota_region_id;
    INSERT INTO city (city_id, name, region_id) VALUES (uuid_generate_v4(), 'La Paz', bogota_region_id), (uuid_generate_v4(), 'El Alto', bogota_region_id);
    INSERT INTO region (region_id, name, country_id) VALUES (uuid_generate_v4(), 'Santa Cruz', bol_id) RETURNING region_id INTO bogota_region_id;
    INSERT INTO city (city_id, name, region_id) VALUES (uuid_generate_v4(), 'Santa Cruz de la Sierra', bogota_region_id);

    -- Uruguay
    INSERT INTO region (region_id, name, country_id) VALUES (uuid_generate_v4(), 'Montevideo', uru_id) RETURNING region_id INTO bogota_region_id;
    INSERT INTO city (city_id, name, region_id) VALUES (uuid_generate_v4(), 'Montevideo', bogota_region_id);

    -- Paraguay
    INSERT INTO region (region_id, name, country_id) VALUES (uuid_generate_v4(), 'Central', par_id) RETURNING region_id INTO bogota_region_id;
    INSERT INTO city (city_id, name, region_id) VALUES (uuid_generate_v4(), 'Asunción', bogota_region_id), (uuid_generate_v4(), 'Luque', bogota_region_id);

    -- Venezuela
    INSERT INTO region (region_id, name, country_id) VALUES (uuid_generate_v4(), 'Distrito Capital', ven_id) RETURNING region_id INTO bogota_region_id;
    INSERT INTO city (city_id, name, region_id) VALUES (uuid_generate_v4(), 'Caracas', bogota_region_id);
    INSERT INTO region (region_id, name, country_id) VALUES (uuid_generate_v4(), 'Zulia', ven_id) RETURNING region_id INTO bogota_region_id;
    INSERT INTO city (city_id, name, region_id) VALUES (uuid_generate_v4(), 'Maracaibo', bogota_region_id);

    -- Costa Rica
    INSERT INTO region (region_id, name, country_id) VALUES (uuid_generate_v4(), 'San José', cri_id) RETURNING region_id INTO bogota_region_id;
    INSERT INTO city (city_id, name, region_id) VALUES (uuid_generate_v4(), 'San José', bogota_region_id);

    -- Panama
    INSERT INTO region (region_id, name, country_id) VALUES (uuid_generate_v4(), 'Panamá', pan_id) RETURNING region_id INTO bogota_region_id;
    INSERT INTO city (city_id, name, region_id) VALUES (uuid_generate_v4(), 'Panamá City', bogota_region_id);

    -- Guatemala
    INSERT INTO region (region_id, name, country_id) VALUES (uuid_generate_v4(), 'Guatemala', gua_id) RETURNING region_id INTO bogota_region_id;
    INSERT INTO city (city_id, name, region_id) VALUES (uuid_generate_v4(), 'Guatemala City', bogota_region_id);

    -- El Salvador
    INSERT INTO region (region_id, name, country_id) VALUES (uuid_generate_v4(), 'San Salvador', els_id) RETURNING region_id INTO bogota_region_id;
    INSERT INTO city (city_id, name, region_id) VALUES (uuid_generate_v4(), 'San Salvador', bogota_region_id);

    -- Honduras
    INSERT INTO region (region_id, name, country_id) VALUES (uuid_generate_v4(), 'Francisco Morazán', hon_id) RETURNING region_id INTO bogota_region_id;
    INSERT INTO city (city_id, name, region_id) VALUES (uuid_generate_v4(), 'Tegucigalpa', bogota_region_id);

    -- Nicaragua
    INSERT INTO region (region_id, name, country_id) VALUES (uuid_generate_v4(), 'Managua', nic_id) RETURNING region_id INTO bogota_region_id;
    INSERT INTO city (city_id, name, region_id) VALUES (uuid_generate_v4(), 'Managua', bogota_region_id);

    -- Cuba
    INSERT INTO region (region_id, name, country_id) VALUES (uuid_generate_v4(), 'La Habana', cub_id) RETURNING region_id INTO bogota_region_id;
    INSERT INTO city (city_id, name, region_id) VALUES (uuid_generate_v4(), 'Havana', bogota_region_id);

    -- Dominican Republic
    INSERT INTO region (region_id, name, country_id) VALUES (uuid_generate_v4(), 'Distrito Nacional', dom_id) RETURNING region_id INTO bogota_region_id;
    INSERT INTO city (city_id, name, region_id) VALUES (uuid_generate_v4(), 'Santo Domingo', bogota_region_id);

END $$;
