-------------------------------------------------
---------- GOAT NEW POIS PREPARATION ------------
-------------------------------------------------

-- This script should not be part of the main application, the resulting database (pois_full_replacement) should be defined before, and this shapefile should be available in the data folder


-- INPUTS
-- Database joins from Establecimientos and 2.4, as schools_input 
-- Add amenity column
SELECT * FROM schools_input WHERE ngenombre LIKE 'esap'
ALTER TABLE schools_input
ADD COLUMN amenity TEXT;

-- Filter universities when join is null

UPDATE schools_input 
SET amenity = 'university' WHERE "09_estab_1" IS NULL AND 
"ngenombre" LIKE ANY (ARRAY['%Universidad%','SENA','Politécnico%','%Universitaria%','Corporación%','%Tecnológica%','%Educación Superior%','Escuela Superior de Administración Pública'])

-- Filter kindergartens when join is null

UPDATE schools_input
SET amenity = 'kindergarten' WHERE "09_estab_1" IS NULL AND "ngenombre" LIKE ANY (ARRAY ['%Jardín Infantil%','%Preescolar%','Psicopedagogico%','%Jardin Infantil%','%Infantil%']);

-- Filter schools (primary - secondary)

UPDATE schools_input
SET amenity = 'schools' WHERE "09_estab_1" IS NULL AND "ngenombre" LIKE ANY (ARRAY ['Academia%','Colegio%,¿Fundacion Colegio%','Fundación Colegio%','Colegio %','Colegio %','Escuela %','%Gimnasio %','Instituto %','Liceo %','Externado %','Centro Comercial%','Institucion Educativa%',
	'Nuevo Colegio%','Nuevo Liceo %','Centro Educativo %'])

	UPDATE schools_input
SET amenity = '' WHERE "09_estab_1" IS NULL AND "ngenombre" LIKE ANY (ARRAY['Escuela Colombiana%','Escuela Mediatica','Escuela Superior%','Escuela de Inteligencia%','Escuela de Logística','Escuela de Salvamento%'])


SELECT * FROM schools_input;
-- Create new database for organized POIS

DROP TABLE IF EXISTS pois_full_replacement;
CREATE TABLE pois_full_replacement (origin_geometry TEXT,ACCESS TEXT, amenity TEXT,"name" TEXT,opening_hours TEXT,geom geometry, wheelchair text);

SELECT count(gid) FROM pois_userinput; -- 62 135
-- ADD new educative 


INSERT INTO pois_full_replacement(

-- 1. Extract Kindergardens

SELECT 'point' AS origin_geometry, NULL AS ACCESS, 'kindergarten' AS amenity, ngenombre AS "name", NULL AS opening_hours, geom, NULL AS wheelchair FROM schools_input
WHERE "09_estab_3" IS NULL AND (ngefuente = 'Secretaria Distrital de Educación  SDE' AND ngenombre LIKE ANY (ARRAY ['%Jardín Infantil%','%Preescolar%','Psicopedagogico%','%Jardin Infantil%','%Infantil%']))
--6
UNION ALL 

SELECT 'point' AS origin_geometry, NULL AS ACCESS, 'kindergarten' AS amenity, ngenombre AS "name", NULL AS opening_hours, geom, NULL AS wheelchair FROM schools_input
WHERE lower("09_estab15") LIKE '%preescolar%'
--1890
UNION ALL 

-- 2. Extract Schools
		-- Schools = 2261 original
		-- filter no matches = 529
		-- extra filter = 1718
SELECT 'point' AS origin_geometry, NULL AS ACCESS, 'school' AS amenity, ngenombre AS "name",NULL AS opening_hours, geom, NULL AS wheelchair FROM schools_input
WHERE "09_estab_3" IS NULL AND (ngefuente = 'Secretaria Distrital de Educación  SDE' AND ngenombre LIKE 
ANY (ARRAY ['Academia%','Colegio%,¿Fundacion Colegio%','Fundación Colegio%','Colegio %','Colegio %','Escuela %','%Gimnasio %','Instituto %','Liceo %','Externado %','Centro Comercial%','Institucion Educativa%',
	'Nuevo Colegio%','Nuevo Liceo %','Centro Educativo %']))
EXCEPT 
SELECT 'point' AS origin_geometry, NULL AS ACCESS, 'school' AS amenity, ngenombre AS "name",NULL AS opening_hours, geom, NULL AS wheelchair FROM schools_input
WHERE "09_estab_3" IS NULL AND (ngefuente = 'Secretaria Distrital de Educación  SDE' AND ngenombre LIKE ANY (ARRAY['Escuela Colombiana%','Escuela Mediatica','Escuela Superior%','Escuela de Inteligencia%','Escuela de Logística','Escuela de Salvamento%']))

UNION ALL

SELECT 'point' AS origin_geometry, NULL AS ACCESS, 'school' AS amenity, ngenombre AS "name",NULL AS opening_hours, geom, NULL AS wheelchair FROM schools_input
WHERE lower("09_estab15") LIKE ANY (ARRAY['%básica primaria%','%básica secundaria%','%media%']) 

-- 3. Extract Universities

UNION ALL

SELECT 'point' AS origin_geometry, NULL AS ACCESS, 'university' AS amenity, ngenombre AS "name",NULL AS opening_hours, geom, NULL AS wheelchair FROM schools_input 
WHERE amenity = 'university'
);

-- ADD SITP (Conventional bus service) stations

INSERT INTO pois_full_replacement(
SELECT 'point' AS origin_geometry, NULL AS ACCESS, 'sitp' AS amenity, nombre_par AS "name", NULL AS opening_hours, geom, NULL AS wheelchair FROM sitp_stops);

-- ADD BRT (Stations (3)and portals(2.3)

INSERT INTO pois_full_replacement(

SELECT 'polygon' AS origin_geometry, NULL AS ACCESS, 'transmilenio' AS amenity, ntrnombre AS "name", 'Mo-Sa 4:30-23:00; Su 6:00-21:00, PH 6:00-21:00' AS opening_hours, geom, 'yes' AS wheelchair FROM transport_nodes

UNION ALL

SELECT 'polygon' AS origin_geometry, NULL AS ACCESS,  'transmilenio' AS amenity, etrnombre AS "name", 'Mo-Sa 4:30-23:00; Su 6:00-21:00, PH 6:00-21:00' AS opening_hours, geom, 'yes' AS wheelchair FROM transmilenio_stations

UNION ALL
-- Notary 
SELECT 'point' AS origin_geometry,  NULL AS ACCESS, 'notary' AS amenity, ngenombre AS "name", NULL, geom, NULL FROM extra_pois WHERE lower(ngenombre) LIKE '%notaría%'

UNION ALL

-- Cade
SELECT 'point' AS origin_geometry,  NULL AS ACCESS, 'cade' AS amenity, ngenombre AS "name", NULL, geom, NULL FROM extra_pois WHERE lower(ngenombre) LIKE '%cade%' AND ngeclasifi = 'FUN-PUB'

);


--END
SELECT * FROM pois_full_replacement;



-- Testing transmicable

INSERT INTO pois_userinput 
SELECT osm_id,'point' as origin_geometry, access,"addr:housenumber" as housenumber, 'transmicable' AS amenity,  
tags -> 'origin' AS origin, tags -> 'organic' AS organic, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, way as geom, tags -> 'wheelchair' as wheelchair  
FROM planet_osm_point
WHERE aerialway ='station' AND public_transport = 'station'

-- End

SELECT * FROM pois_userinput pu WHERE amenity = 'park' AND ACCESS IS NOT NULL;

SELECT * FROM planet_osm_polygon WHERE leisure = 'park' AND (ACCESS IS NULL OR ACCESS='public')

-- Testing parks

INSERT INTO pois_userinput
SELECT osm_id,'polygon' as origin_geometry, access,"addr:housenumber" as housenumber, 'park' AS amenity,  
tags -> 'origin' AS origin, tags -> 'organic' AS organic, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, ST_Centroid(way) as geom, tags -> 'wheelchair' as wheelchair  
FROM planet_osm_polygon
WHERE leisure = 'park' AND (ACCESS IS NULL OR ACCESS='public')


SELECT * FROM pois_full_replacement;