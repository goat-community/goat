DROP TABLE IF EXISTS pois;
CREATE TABLE pois as (

SELECT osm_id,'point' as orgin_geometry, access,"addr:housenumber" as housenumber, amenity, shop, 
tags -> 'origin' AS origin, tags -> 'organic' AS organic, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, way as geom
FROM planet_osm_point
WHERE amenity IS NOT NULL AND shop IS NULL AND amenity <> 'school'

UNION ALL 

SELECT osm_id,'point' as orgin_geometry, access,"addr:housenumber" as housenumber, amenity, shop, 
tags -> 'origin' AS origin, tags -> 'organic' AS organic, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, way as geom
FROM planet_osm_point
WHERE shop IS NOT NULL AND amenity IS NULL

UNION ALL 

SELECT osm_id, 'polygon' as orgin_geometry, access,"addr:housenumber" as housenumber, amenity, shop, 
tags -> 'origin' AS origin, tags -> 'organic' AS organic, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, st_centroid(way) as geom
FROM planet_osm_polygon
WHERE amenity IS NOT NULL AND amenity <> 'school' 

UNION ALL 

SELECT osm_id,'polygon' as orgin_geometry, access,"addr:housenumber" as housenumber, amenity, 
shop, tags -> 'origin' AS origin, tags -> 'organic' AS organic, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, st_centroid(way) as geom
FROM planet_osm_polygon
WHERE shop IS NOT NULL 


UNION ALL

SELECT osm_id,'point' as orgin_geometry, access,"addr:housenumber" as housenumber, tourism, shop, 
tags -> 'origin' AS origin, tags -> 'organic' AS organic, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, way as geom
FROM planet_osm_point
WHERE tourism IS NOT NULL


UNION ALL 

SELECT * FROM (
SELECT osm_id, 'polygon' as orgin_geometry, access,"addr:housenumber" as housenumber, amenity, shop, 
tags -> 'origin' AS origin, tags -> 'organic' AS organic, denomination,brand,name,
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
SELECT osm_id,'point' as orgin_geometry, access,"addr:housenumber" as housenumber, amenity, shop, 
tags -> 'origin' AS origin, tags -> 'organic' AS organic, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, way as geom
FROM planet_osm_point
WHERE amenity = 'school') x
WHERE lower(name)~~ ANY('{%grundschule%,%hauptschule%,%realschule%,%mittelschule%,%gymnasium%}')   
);

UPDATE pois set amenity = 'primary_school'
WHERE amenity = 'school' 
AND lower(name)~~ '%grundschule%';

UPDATE pois set amenity = 'secondary_school'
WHERE amenity = 'school' 
AND lower(name)~~ ANY('{%hauptschule%,%realschule%,%mittelschule%,%gymnasium%}');


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

--Refinement Shopping

UPDATE pois SET amenity = 'discount_supermarket'
WHERE lower(name)~~ 
ANY
(
	SELECT concat(concat('%',lower(unnest(variable_array))),'%') 
	FROM variable_container WHERE identifier = 'chains_discount_supermarket'
)  
AND amenity = 'supermarket';

UPDATE pois SET amenity = 'hypermarket'
WHERE lower(name)~~ 
ANY
(
	SELECT concat(concat('%',lower(unnest(variable_array))),'%') 
	FROM variable_container WHERE identifier = 'chains_hypermarket'
)  
AND amenity = 'supermarket';

UPDATE pois SET amenity = 'no_end_consumer_store'
WHERE lower(name)~~ 
ANY
(
	SELECT concat(concat('%',lower(unnest(variable_array))),'%') 
	FROM variable_container WHERE identifier = 'no_end_consumer_store'
)  
AND amenity = 'supermarket';

UPDATE pois SET amenity = 'health_food'
WHERE lower(name)~~ 
ANY
(
	SELECT concat(concat('%',lower(unnest(variable_array))),'%') 
	FROM variable_container WHERE identifier = 'chains_health_food'
)  
AND amenity = 'supermarket';


UPDATE pois SET amenity = 'organic'
WHERE organic = 'only'
AND amenity = 'supermarket';

UPDATE pois SET amenity = 'international_supermarket'
WHERE origin is not null
AND amenity = 'supermarket';

--------------------------------------------------------------------------
--Create first pois as it is continuing with gid----------------------------
--------------------------------------------------------------------------

--Create public_transport_stops
DROP TABLE IF EXISTS public_transport_stops;
SELECT *, 'point' as orgin_geometry,(SELECT max(gid) FROM pois) + row_number() over() as gid
INTO public_transport_stops FROM (
SELECT osm_id,'bus_stop' as public_transport_stop,name,way as geom FROM planet_osm_point 
WHERE highway = 'bus_stop' AND name IS NOT NULL
UNION ALL
SELECT osm_id,'bus_stop' as public_transport_stop,name,way as geom FROM planet_osm_point 
WHERE public_transport = 'platform' AND name IS NOT NULL AND tags -> 'bus'='yes'
UNION ALL
SELECT osm_id,'tram_stop' as public_transport_stop,name,way as geom FROM planet_osm_point 
WHERE public_transport = 'stop_position' 
AND tags -> 'tram'='yes'
AND name IS NOT NULL
UNION ALL
SELECT osm_id,'subway_entrance' as public_transport,name, way as geom FROM planet_osm_point
WHERE railway = 'subway_entrance'
UNION ALL
SELECT osm_id,'rail_station' as public_transport,name,way as geom 
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
