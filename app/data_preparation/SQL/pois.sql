DROP TABLE IF EXISTS pois;
CREATE TABLE pois as (

SELECT osm_id, access,"addr:housenumber" as housenumber, amenity, shop, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, way as geom
FROM planet_osm_point
WHERE amenity IS NOT NULL AND shop IS NULL AND amenity <> 'school'

UNION ALL 

SELECT osm_id, access,"addr:housenumber" as housenumber, amenity, shop, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, way as geom
FROM planet_osm_point
WHERE shop IS NOT NULL AND amenity IS NULL

UNION ALL 

SELECT osm_id, access,"addr:housenumber" as housenumber, amenity, shop, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, st_centroid(way) as geom
FROM planet_osm_polygon
WHERE amenity IS NOT NULL AND amenity <> 'school' 

UNION ALL 

SELECT osm_id, access,"addr:housenumber" as housenumber, amenity, shop, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, st_centroid(way) as geom
FROM planet_osm_polygon
WHERE shop IS NOT NULL 


UNION ALL

SELECT osm_id, access,"addr:housenumber" as housenumber, tourism, shop, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, way as geom
FROM planet_osm_point
WHERE tourism IS NOT NULL


UNION ALL 

SELECT * FROM (
SELECT osm_id, access,"addr:housenumber" as housenumber, amenity, shop, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, st_centroid(way) as geom
FROM planet_osm_polygon
WHERE amenity = 'school') x
WHERE name LIKE '%Grundschule%'
OR name like 'gymnasium' 
OR name like '%Mittelschule%' 
OR name like '%Realschule%'
OR name like '%Haupt%'

UNION ALL 

SELECT * FROM (
SELECT osm_id, access,"addr:housenumber" as housenumber, amenity, shop, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, way as geom
FROM planet_osm_point
WHERE amenity = 'school') x
WHERE name LIKE '%Grundschule%'
OR name like '%gymnasium%' 
OR name like '%Mittelschule%' 
OR name like '%Haupt%'
OR name like '%Realschule%'
);



UPDATE pois set amenity = 'primary_school'
WHERE amenity = 'school' 
AND name LIKE '%Grundschule%';

UPDATE pois set amenity = 'secondary_school'
WHERE amenity = 'school' 
AND name like '%gymnasium%' 
OR name like '%Mittelschule%' 
OR name like '%Haupt%'
OR name like '%Realschule%';


--For Munich grocery == convencience
UPDATE pois set shop = 'convenience'
WHERE shop ='grocery';

UPDATE pois set shop = 'clothes'
WHERE shop ='fashion';


ALTER TABLE pois add column gid serial;

ALTER TABLE pois add primary key(gid); 


CREATE INDEX index_pois ON pois USING GIST (geom);

