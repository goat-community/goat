-------------------------------------------------
---------- GOAT NEW POIS PREPARATION ------------
-------------------------------------------------

-- INPUTS
-- Database joins from Establecimientos and 2.4, as schools_input 
-- Add amenity column

ALTER TABLE schools_input
ADD COLUMN amenity TEXT;

-- Filter universities when join is null

UPDATE schools_input 
SET amenity = 'university' WHERE "09_estab_1" IS NULL AND 
"ngenombre" LIKE ANY (ARRAY['%Universidad%','SENA','Politécnico%','%Universitaria%','Corporación%','%Tecnológica%','%Educación Superior%'])

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
CREATE TABLE pois_full_replacement (origin_geometry TEXT, amenity TEXT,"name" TEXT,opening_hours TEXT,geom geometry, wheelchair text);

-- ADD new schools

INSERT INTO pois_full_replacement(

-- 1. Extract Kindergardens

SELECT 'point' AS origin_geometry, 'kindergarten' AS amenity, "NGeNombre" AS "name",NULL AS opening_hours, geom, NULL AS wheelchair FROM new_amenities
WHERE "NGeFuente" = 'Secretaria Distrital de Educación  SDE' AND "NGeNombre" LIKE ANY (ARRAY ['%Jardín Infantil%','%Preescolar%','Psicopedagogico%','%Jardin Infantil%','%Infantil%'])

UNION ALL 

-- 2. Extract Schools

SELECT 'point' AS origin_geometry, 'school' AS amenity, "NGeNombre" AS "name",NULL AS opening_hours, geom, NULL AS wheelchair FROM new_amenities 
WHERE "NGeFuente" = 'Secretaria Distrital de Educación  SDE' AND "NGeNombre" LIKE 
ANY (ARRAY ['Academia%','Colegio%,¿Fundacion Colegio%','Fundación Colegio%','Colegio %','Colegio %','Escuela %','%Gimnasio %','Instituto %','Liceo %','Externado %','Centro Comercial%','Institucion Educativa%',
	'Nuevo Colegio%','Nuevo Liceo %','Centro Educativo %'])
EXCEPT 
SELECT 'point' AS origin_geometry, 'school' AS amenity, "NGeNombre" AS "name",NULL AS opening_hours, geom, NULL AS wheelchair FROM new_amenities
WHERE "NGeFuente" = 'Secretaria Distrital de Educación  SDE' AND "NGeNombre" LIKE ANY (ARRAY['Escuela Colombiana%','Escuela Mediatica','Escuela Superior%','Escuela de Inteligencia%','Escuela de Logística','Escuela de Salvamento%'])

-- 3. Extract Universities

UNION ALL

SELECT 'point' AS origin_geometry, 'university' AS amenity, "NGeNombre" AS "name",NULL AS opening_hours, geom, NULL AS wheelchair FROM new_amenities 
WHERE "NGeFuente" = 'Secretaria Distrital de Educación  SDE' AND "NGeNombre" LIKE ANY (ARRAY['%Universidad%','SENA','Politécnico%','%Universitaria%'])
EXCEPT 
SELECT 'point' AS origin_geometry, 'university' AS amenity, "NGeNombre" AS "name", NULL AS opening_hours, geom, NULL AS wheelchair FROM new_amenities
WHERE 
"NGeFuente" = 'Secretaria Distrital de Educación  SDE' AND "NGeNombre" LIKE ANY (ARRAY['Colegio%','Jardin%','Liceo'])
);

-- ADD SITP (Conventional bus service) stations

INSERT INTO pois_full_replacement(
SELECT 'point' AS origin_geometry, 'sitp' AS amenity, nombre_par AS "name", NULL AS opening_hours, geom, NULL AS wheelchair FROM sitp_stops);

-- ADD BRT (Stations (3)and portals(2.3)

INSERT INTO pois_full_replacement(

SELECT 'polygon' AS origin_geometry, 'transmilenio' AS amenity, ntrnombre AS "name", 'Mo-Sa 4:30-23:00; Su 6:00-21:00, PH 6:00-21:00' AS opening_hours, geom, 'yes' AS wheelchair FROM transport_nodes

UNION ALL

SELECT 'polygon' AS origin_geometry, 'transmilenio' AS amenity, etrnombre AS "name", 'Mo-Sa 4:30-23:00; Su 6:00-21:00, PH 6:00-21:00' AS opening_hours, geom, 'yes' AS wheelchair FROM transmilenio_stations

UNION ALL
-- Notary 
SELECT 'point' AS origin_geometry, 'notary' AS amenity, ngenombre AS "name", NULL, geom, NULL FROM extra pois WHERE lower(ngenombre) LIKE '%notaría%'

UNION ALL

-- Cade
SELECT 'point' AS origin_geometry, 'cade' AS amenity, ngenombre AS "name", NULL, geom, NULL FROM extra pois WHERE lower(ngenombre) LIKE '%cade%' AND ngeclasifi = 'FUN-PUB'

);


--END




-- Testing transmicable

INSERT INTO pois_userinput 
SELECT osm_id,'point' as origin_geometry, access,"addr:housenumber" as housenumber, 'transmicable' AS amenity,  
tags -> 'origin' AS origin, tags -> 'organic' AS organic, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, way as geom, tags -> 'wheelchair' as wheelchair  
FROM planet_osm_point
WHERE aerialway ='station' AND public_transport = 'station'

-- End

