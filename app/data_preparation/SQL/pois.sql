<<<<<<< HEAD
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

--Select relevant operators bicycle_rental

DELETE FROM pois 
WHERE (NOT lower(operator) ~~ 
ANY
(
	SELECT concat(concat('%',lower(unnest(variable_array))),'%') 
	FROM variable_container WHERE identifier = 'operators_bicycle_rental'
)  
OR operator IS NULL) 
AND amenity = 'bicycle_rental';

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
=======
DROP TABLE IF EXISTS pois;
CREATE TABLE pois as (


-- all amenities, excluding shops, schools and kindergartens
SELECT osm_id,'point' as orgin_geometry, access,"addr:housenumber" as housenumber, amenity, shop, 
tags -> 'origin' AS origin, tags -> 'organic' AS organic, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, way as geom
FROM planet_osm_point
WHERE amenity IS NOT NULL AND shop IS NULL AND amenity <> 'school' AND amenity <> 'kindergarten'

UNION ALL 
-- all shops that don't have an amenity'
SELECT osm_id,'point' as orgin_geometry, access,"addr:housenumber" as housenumber, amenity, shop, 
tags -> 'origin' AS origin, tags -> 'organic' AS organic, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, way as geom
FROM planet_osm_point
WHERE shop IS NOT NULL AND amenity IS NULL

UNION ALL 
-- all amenities that are not schools
SELECT osm_id, 'polygon' as orgin_geometry, access,"addr:housenumber" as housenumber, amenity, shop, 
tags -> 'origin' AS origin, tags -> 'organic' AS organic, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, st_centroid(way) as geom
FROM planet_osm_polygon
WHERE amenity IS NOT NULL AND amenity <> 'school' AND amenity <> 'kindergarten'

UNION ALL 
-- all shops
SELECT osm_id,'polygon' as orgin_geometry, access,"addr:housenumber" as housenumber, amenity, 
shop, tags -> 'origin' AS origin, tags -> 'organic' AS organic, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, st_centroid(way) as geom
FROM planet_osm_polygon
WHERE shop IS NOT NULL 


UNION ALL
-- all tourism
SELECT osm_id,'point' as orgin_geometry, access,"addr:housenumber" as housenumber, tourism, shop, 
tags -> 'origin' AS origin, tags -> 'organic' AS organic, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, way as geom
FROM planet_osm_point
WHERE tourism IS NOT NULL


UNION ALL 


-------------------------------------------------------------------
--------------------School polygons--------------------------------
-------------------------------------------------------------------

--------------------------primary_school (über Name, wenn kein isced:level)------------------
CREATE TABLE schools_from_polygons AS
SELECT * FROM (
SELECT osm_id, 'polygon' as orgin_geometry, access,"addr:housenumber" as housenumber, 'primary_school' AS amenity, shop, 
tags -> 'origin' AS origin, tags -> 'organic' AS organic, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, st_centroid(way) as geom
FROM planet_osm_polygon
WHERE amenity = 'school') x

WHERE (lower(name) LIKE '%grund-%'
OR name like '%Grund %'
OR lower(name) like '%grundsch%'
AND lower(name) NOT LIKE '%grund-schule%'
AND tags -> 'isced:level' IS NULL)
OR tags -> 'isced:level' LIKE '1'

UNION ALL


--------------secondary_school; Haupt-/Mittel-/Realschule/Gymnasium (über Name, wenn kein isced:level)----------------
SELECT * FROM (
SELECT osm_id, 'polygon' as orgin_geometry, access,"addr:housenumber" as housenumber, 'secondary_school' AS amenity, shop, 
tags -> 'origin' AS origin, tags -> 'organic' AS organic, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, st_centroid(way) as geom
FROM planet_osm_polygon
WHERE amenity = 'school') x

WHERE (lower(name) LIKE '%haupt-%'
OR name like '%Haupt %'
OR lower(name) like '%hauptsch%'
AND lower(name) NOT LIKE '%haupt-schule%'

OR lower(name) like '%mittel-%'
OR name like '%Mittel %'
OR lower(name) like '%mittelsch%'
AND lower(name) NOT LIKE '%mittel-schule%'

OR lower(name) like '%real-%'
OR name like '%Real %'
OR lower(name) like '%realsch%'
AND lower(name) NOT LIKE '%real-schule%'

OR lower(name) like '%förder-%'
OR name like '%Förder %'
OR lower(name) like '%fördersch%'
AND lower(name) NOT LIKE '%förder-schule%'

OR lower(name) like '%gesamt-%'
OR name like '%Gesamt %'
OR lower(name) like '%gesamtsch%'
AND lower(name) NOT LIKE '%gesamt-schule%'

OR lower(name) like '%-gymnasium%'
OR lower(name) like '%gymnasium-%'
OR name like '% Gymnasium%'
OR name like '%Gymnasium %'

OR name like '%Fachobersch%'

AND tags -> 'isced:level' IS NULL)

OR tags -> 'isced:level' LIKE '2'
OR tags -> 'isced:level' LIKE '3'

UNION ALL 

-----------------------------------------------------------------
--------------------School points--------------------------------
-----------------------------------------------------------------

--------------------------primary_school (über Name, wenn kein isced:level)------------------
CREATE TABLE schools_from_points AS
SELECT * FROM (
SELECT osm_id, 'point' as orgin_geometry, access,"addr:housenumber" as housenumber, 'primary_school' AS amenity, shop, 
tags -> 'origin' AS origin, tags -> 'organic' AS organic, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, st_centroid(way) as geom
FROM planet_osm_point
WHERE amenity = 'school') x

WHERE (lower(name) LIKE '%grund-%'
OR name like '%Grund %'
OR lower(name) like '%grundsch%'
AND lower(name) NOT LIKE '%grund-schule%'
AND tags -> 'isced:level' IS NULL)
OR tags -> 'isced:level' LIKE '1'

UNION ALL


--------------secondary_school; Haupt-/Mittel-/Realschule/Gymnasium (über Name, wenn kein isced:level)----------------
SELECT * FROM (
SELECT osm_id, 'point' as orgin_geometry, access,"addr:housenumber" as housenumber, 'secondary_school' AS amenity, shop, 
tags -> 'origin' AS origin, tags -> 'organic' AS organic, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, st_centroid(way) as geom
FROM planet_osm_point
WHERE amenity = 'school') x

WHERE (lower(name) LIKE '%haupt-%'
OR name like '%Haupt %'
OR lower(name) like '%hauptsch%'
AND lower(name) NOT LIKE '%haupt-schule%'

OR lower(name) like '%mittel-%'
OR name like '%Mittel %'
OR lower(name) like '%mittelsch%'
AND lower(name) NOT LIKE '%mittel-schule%'

OR lower(name) like '%real-%'
OR name like '%Real %'
OR lower(name) like '%realsch%'
AND lower(name) NOT LIKE '%real-schule%'

OR lower(name) like '%förder-%'
OR name like '%Förder %'
OR lower(name) like '%fördersch%'
AND lower(name) NOT LIKE '%förder-schule%'

OR lower(name) like '%gesamt-%'
OR name like '%Gesamt %'
OR lower(name) like '%gesamtsch%'
AND lower(name) NOT LIKE '%gesamt-schule%'

OR lower(name) like '%-gymnasium%'
OR lower(name) like '%gymnasium-%'
OR name like '% Gymnasium%'
OR name like '%Gymnasium %'

OR name like '%Fachobersch%'

AND tags -> 'isced:level' IS NULL)

OR tags -> 'isced:level' LIKE '2'
OR tags -> 'isced:level' LIKE '3'

UNION ALL 


-----------------------------------------------------------------
-------------Insert kindergartens--------------------------------
-----------------------------------------------------------------

DROP TABLE IF EXISTS merged_kindergartens;
CREATE TEMP TABLE merged_kindergartens AS
(
	WITH merged_geom AS
	(	
		SELECT (ST_Dump(way)).geom
		FROM (
			SELECT ST_Union(way) AS way		
			FROM planet_osm_polygon
			WHERE amenity = 'kindergarten') x
	)	
	-- Get attributes back by getting all polygons that are within the merged geometry.
	-- Group by the merged geometry. Aggregate all other attributes...
	SELECT max(osm_id) AS osm_id, 'polygon' as orgin_geometry, max(access) AS access, max("addr:housenumber") AS "addr:housenumber",
	max(amenity) AS amenity, max(shop) AS shop, max(tags -> 'origin') AS origin, max(tags -> 'organic') AS organic, max(denomination) AS denomination,
	max(brand) AS brand, max(name) AS name, max(operator) AS operator, max(public_transport) AS public_transport, max(railway) AS railway,
	max(religion) AS religion, max(tags -> 'opening_hours') AS opening_hours, max(REF) AS ref, max(tags::TEXT)::hstore AS tags, m.geom
	FROM planet_osm_polygon p, merged_geom m
	WHERE amenity = 'kindergarten' AND st_contains(m.geom, p.way)
	GROUP BY m.geom
);


INSERT INTO pois
		
SELECT DISTINCT p.osm_id,'point' as orgin_geometry, p.access, 'addr:housenumber', p.amenity, p.shop, --p."addr:housenumber" doesn't work
p.tags -> 'origin' AS origin, p.tags -> 'organic' AS organic, p.denomination,p.brand,p.name,
p.operator,p.public_transport,p.railway,p.religion,p.tags -> 'opening_hours' as opening_hours, p.ref, p.tags::hstore AS tags, p.way as geom
FROM planet_osm_point p, merged_kindergartens
WHERE p.amenity = 'kindergarten' AND NOT st_within(p.way, merged_kindergartens.geom)

UNION ALL

SELECT osm_id,'polygon' as orgin_geometry, access, "addr:housenumber", amenity, shop, 
tags -> 'origin' AS origin, tags -> 'organic' AS organic, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, st_centroid(geom) AS geom
FROM merged_kindergartens;

------------------------------------------end kindergarten-------------------------------------------








--For Munich grocery == convencience
UPDATE pois set shop = 'convenience'
WHERE shop ='grocery';

UPDATE pois set shop = 'clothes'
WHERE shop ='fashion';

ALTER TABLE pois add column gid serial;
ALTER TABLE pois add primary key(gid); 
CREATE INDEX index_pois ON pois USING GIST (geom);
CREATE INDEX ON pois(amenity);

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

--Select relevant operators bicycle_rental

DELETE FROM pois 
WHERE (NOT lower(operator) ~~ 
ANY
(
	SELECT concat(concat('%',lower(unnest(variable_array))),'%') 
	FROM variable_container WHERE identifier = 'operators_bicycle_rental'
)  
OR operator IS NULL) 
AND amenity = 'bicycle_rental';

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
>>>>>>> 7b22c69a... Better selection of schools.
