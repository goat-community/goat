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

UPDATE pois SET amenity = shop
WHERE shop IS NOT NULL;

ALTER TABLE pois DROP COLUMN shop;


--------------------------------------------------------------------------
--Create first pois as it is continuing with gid----------------------------
--------------------------------------------------------------------------

--Create public_transport_stops
DROP TABLE IF EXISTS public_transport_stops;
SELECT *, (SELECT max(gid) FROM pois) + row_number() over() as gid
INTO public_transport_stops FROM (
SELECT 'bus_stop' as public_transport_stop,name,way as geom FROM planet_osm_point 
WHERE highway = 'bus_stop' AND name IS NOT NULL
UNION ALL
SELECT 'bus_stop' as public_transport_stop,name,way as geom FROM planet_osm_point 
WHERE public_transport = 'platform' AND name IS NOT NULL AND tags -> 'bus'='yes'
UNION ALL
SELECT 'tram_stop' as public_transport_stop,name,way as geom FROM planet_osm_point 
WHERE public_transport = 'stop_position' 
AND tags -> 'tram'='yes'
AND name IS NOT NULL
UNION ALL
SELECT  'subway_entrance' as public_transport,name, way as geom FROM planet_osm_point
WHERE railway = 'subway_entrance'
UNION ALL
SELECT 'sbahn_regional' as public_transport,name,way as geom 
FROM planet_osm_point WHERE railway = 'stop'
AND tags -> 'train' ='yes') x;



UPDATE public_transport_stops set name = x.name 
FROM
(SELECT p.geom,x.name,min(st_distance(p.geom::geography,x.geom::geography))
FROM public_transport_stops p,
	(SELECT 'subway' as public_transport,name,way as geom  FROM planet_osm_point 
	WHERE public_transport ='station' AND
	tags -> 'subway' = 'yes' AND railway <> 'proposed') x
WHERE st_dwithin(p.geom::geography,x.geom::geography,500)
GROUP BY p.geom,x.name) x
WHERE public_transport_stops.geom = x.geom
AND public_transport_stop = 'subway_entrance';



ALTER TABLE public_transport_stops add primary key (gid); 
CREATE INDEX index_public_transport_stops ON public_transport_stops USING GIST (geom);
