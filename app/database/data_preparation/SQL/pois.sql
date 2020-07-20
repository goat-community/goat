DROP TABLE IF EXISTS pois CASCADE;
CREATE TABLE pois as (


-- all amenities, excluding shops, schools and kindergartens
SELECT osm_id,'point' as origin_geometry, access,"addr:housenumber" as housenumber, amenity, shop, 
tags -> 'origin' AS origin, tags -> 'organic' AS organic, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, way as geom, tags -> 'wheelchair' as wheelchair  
FROM planet_osm_point
WHERE amenity IS NOT NULL AND shop IS NULL AND amenity <> 'school' AND amenity <> 'kindergarten'

UNION ALL
-- same block to edit--

--all playgrounds (insert leisure as amenity)

SELECT osm_id,'point' as origin_geometry, access,"addr:housenumber" as housenumber, leisure AS amenity, shop, 
tags -> 'origin' AS origin, tags -> 'organic' AS organic, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, way as geom, tags -> 'wheelchair' as wheelchair  
FROM planet_osm_point
WHERE leisure = 'playground'

UNION ALL

SELECT osm_id,'polygon' as origin_geometry, access,"addr:housenumber" as housenumber, leisure AS amenity, shop, 
tags -> 'origin' AS origin, tags -> 'organic' AS organic, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, st_centroid(way) as geom, tags -> 'wheelchair' as wheelchair  
FROM planet_osm_polygon
WHERE leisure = 'playground'

--end same block

UNION ALL 
-- all shops that don't have an amenity'
SELECT osm_id,'point' as origin_geometry, access,"addr:housenumber" as housenumber, amenity, shop, 
tags -> 'origin' AS origin, tags -> 'organic' AS organic, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, way as geom, tags -> 'wheelchair' as wheelchair  
FROM planet_osm_point
WHERE shop IS NOT NULL AND amenity IS NULL

UNION ALL 
-- all amenities that are not schools
SELECT osm_id, 'polygon' as origin_geometry, access,"addr:housenumber" as housenumber, amenity, shop, 
tags -> 'origin' AS origin, tags -> 'organic' AS organic, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, st_centroid(way) as geom, tags -> 'wheelchair' as wheelchair  
FROM planet_osm_polygon
WHERE amenity IS NOT NULL AND amenity <> 'school' AND amenity <> 'kindergarten'

UNION ALL 
-- all shops
SELECT osm_id,'polygon' as origin_geometry, access,"addr:housenumber" as housenumber, amenity, shop, 
tags -> 'origin' AS origin, tags -> 'organic' AS organic, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, st_centroid(way) as geom, tags -> 'wheelchair' as wheelchair  
FROM planet_osm_polygon
WHERE shop IS NOT NULL 

UNION ALL
-- all tourism
SELECT osm_id,'point' as origin_geometry, access,"addr:housenumber" as housenumber, tourism, shop, 
tags -> 'origin' AS origin, tags -> 'organic' AS organic, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, way as geom, tags -> 'wheelchair' as wheelchair  
FROM planet_osm_point
WHERE tourism IS NOT NULL

UNION ALL

-- all sports (sport stuff is usually not tagged with amenity, but with leisure=* and sport=*)

SELECT osm_id,'point' as origin_geometry, access,"addr:housenumber" as housenumber, 'sport' AS amenity, shop, 
tags -> 'origin' AS origin, tags -> 'organic' AS organic, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref, tags||hstore('sport', sport)||hstore('leisure', leisure)  AS tags, way as geom,
tags -> 'wheelchair' as wheelchair  
FROM planet_osm_point
WHERE (sport IS NOT NULL
OR leisure = any (SELECT (jsonb_array_elements_text((select_from_variable_container_o('amenity_config')->'leisure'->'add')::jsonb))))
AND leisure !=(SELECT (jsonb_array_elements_text((select_from_variable_container_o('amenity_config')->'leisure'->'discard')::jsonb)))
AND sport !=(SELECT (jsonb_array_elements_text((select_from_variable_container_o('amenity_config')->'sport'->'discard')::jsonb)))

UNION ALL

SELECT osm_id,'polygon' as origin_geometry, access,"addr:housenumber" as housenumber, 'sport' AS amenity, shop, 
tags -> 'origin' AS origin, tags -> 'organic' AS organic, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref, tags||hstore('sport', sport)||hstore('leisure', leisure)  AS tags, st_centroid(way) as geom,
tags -> 'wheelchair' as wheelchair  
FROM planet_osm_polygon
WHERE (sport IS NOT NULL
OR leisure = any (SELECT (jsonb_array_elements_text((select_from_variable_container_o('amenity_config')->'leisure'->'add')::jsonb))))
AND leisure !=(SELECT (jsonb_array_elements_text((select_from_variable_container_o('amenity_config')->'leisure'->'discard')::jsonb)))
AND sport !=(SELECT (jsonb_array_elements_text((select_from_variable_container_o('amenity_config')->'sport'->'discard')::jsonb)))

UNION ALL 

-- Add fitness centers
SELECT osm_id,'point' as origin_geometry, access,"addr:housenumber" as housenumber, 'gym' AS amenity, shop, 
tags -> 'origin' AS origin, tags -> 'organic' AS organic, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref, tags||hstore('sport', sport)||hstore('leisure', leisure)  AS tags, way as geom,
tags -> 'wheelchair' as wheelchair  
FROM planet_osm_point 
WHERE (leisure = 'fitness_centre' OR (leisure = 'sports_centre' AND sport = 'fitness'))
AND (sport IN('multi','fitness') OR sport IS NULL)
AND NOT (lower(name) LIKE '%yoga%')

UNION ALL 
-- Add Yoga centers

SELECT osm_id,'point' as origin_geometry, access,"addr:housenumber" as housenumber, 'yoga' AS amenity, shop, 
tags -> 'origin' AS origin, tags -> 'organic' AS organic, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref, tags||hstore('sport', sport)||hstore('leisure', leisure)  AS tags, way as geom,
tags -> 'wheelchair' as wheelchair
FROM planet_osm_point WHERE (sport = 'yoga' OR lower(name) LIKE '%yoga%') AND shop IS NULL

UNION ALL 

-------------------------------------------------------------------
--------------------School polygons--------------------------------
-------------------------------------------------------------------

--------------------------primary_school (über Name, wenn kein isced:level)------------------
SELECT osm_id, 'polygon' as origin_geometry, access,"addr:housenumber" as housenumber, 'primary_school' AS amenity, shop, 
tags -> 'origin' AS origin, tags -> 'organic' AS organic, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, st_centroid(way) as geom,
tags -> 'wheelchair' as wheelchair  
FROM planet_osm_polygon
WHERE amenity = 'school' AND (
lower(name) LIKE ANY (SELECT (jsonb_array_elements_text((select_from_variable_container_o('amenity_config')->'primary_school'->'add')::jsonb))) AND
lower(name) NOT LIKE ANY (SELECT (jsonb_array_elements_text((select_from_variable_container_o('amenity_config')->'primary_school'->'discard')::jsonb)))
AND tags -> 'isced:level' IS NULL)
OR tags -> 'isced:level' LIKE '%1%'

UNION ALL


--------------secondary_school; Haupt-/Mittel-/Realschule/Gymnasium (über Name, wenn kein isced:level)----------------

SELECT osm_id, 'polygon' as origin_geometry, access,"addr:housenumber" as housenumber, 'secondary_school' AS amenity, shop, 
tags -> 'origin' AS origin, tags -> 'organic' AS organic, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, st_centroid(way) as geom,
tags -> 'wheelchair' as wheelchair  
FROM planet_osm_polygon
WHERE amenity = 'school' AND ((
lower(name) LIKE ANY (SELECT (jsonb_array_elements_text((select_from_variable_container_o('amenity_config')->'secondary_school'->'add')::jsonb)))
AND
lower(name) NOT LIKE ANY (SELECT (jsonb_array_elements_text((select_from_variable_container_o('amenity_config')->'secondary_school'->'discard')::jsonb)))
AND tags -> 'isced:level' IS NULL
)
OR tags -> 'isced:level' LIKE ANY (ARRAY['%2%', '%3%'])
)

UNION ALL 

-----------------------------------------------------------------
--------------------School points--------------------------------
-----------------------------------------------------------------

--------------------------primary_school (über Name, wenn kein isced:level)------------------

SELECT osm_id, 'point' as origin_geometry, access,"addr:housenumber" as housenumber, 'primary_school' AS amenity, shop, 
tags -> 'origin' AS origin, tags -> 'organic' AS organic, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, st_centroid(way) as geom,
tags -> 'wheelchair' as wheelchair  
FROM planet_osm_point
WHERE amenity = 'school' AND (
lower(name) LIKE ANY (SELECT (jsonb_array_elements_text((select_from_variable_container_o('amenity_config')->'primary_school'->'add')::jsonb))) AND
lower(name) NOT LIKE ANY (SELECT (jsonb_array_elements_text((select_from_variable_container_o('amenity_config')->'primary_school'->'discard')::jsonb)))
AND tags -> 'isced:level' IS NULL)
OR tags -> 'isced:level' LIKE '%1%'

UNION ALL

--------------secondary_school; Haupt-/Mittel-/Realschule/Gymnasium (über Name, wenn kein isced:level)----------------

SELECT osm_id, 'point' as origin_geometry, access,"addr:housenumber" as housenumber, 'secondary_school' AS amenity, shop, 
tags -> 'origin' AS origin, tags -> 'organic' AS organic, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, st_centroid(way) as geom,
tags -> 'wheelchair' as wheelchair  
FROM planet_osm_point
WHERE amenity = 'school' AND ((
lower(name) LIKE ANY (SELECT (jsonb_array_elements_text((select_from_variable_container_o('amenity_config')->'secondary_school'->'add')::jsonb)))
AND
lower(name) NOT LIKE ANY (SELECT (jsonb_array_elements_text((select_from_variable_container_o('amenity_config')->'secondary_school'->'discard')::jsonb)))
AND tags -> 'isced:level' IS NULL
)
OR tags -> 'isced:level' LIKE ANY (ARRAY['%2%', '%3%'])
)
);

-----------------------------------------------------------------
-------------Insert kindergartens--------------------------------
-----------------------------------------------------------------

DROP TABLE IF EXISTS kindergartens_polygons;
CREATE TEMP TABLE kindergartens_polygons AS (
SELECT osm_id,'polygon' as origin_geometry, access, "addr:housenumber" as housenumber, amenity, shop, 
tags -> 'origin' AS origin, tags -> 'organic' AS organic, denomination, brand, name,
operator, public_transport, railway, religion, tags -> 'opening_hours' as opening_hours, ref, tags::hstore AS tags, way as geom,
tags -> 'wheelchair' as wheelchair, ST_centroid(way) AS centroid
FROM planet_osm_polygon
WHERE amenity = 'kindergarten' );

DROP TABLE IF EXISTS kindergarten_duplicates;
CREATE TEMP TABLE kindergarten_duplicates AS (
SELECT *
FROM (
	SELECT o.*, ST_Distance(o.centroid,p.centroid) AS distance
	FROM kindergartens_polygons o
	JOIN kindergartens_polygons p
	ON ST_DWithin( o.centroid::geography, p.centroid::geography, select_from_variable_container_s('duplicated_kindergarden_lookup_radius')::float)
	AND NOT ST_DWithin(o.centroid, p.centroid, 0)
	) AS duplicates) ;

DELETE FROM kindergartens_polygons WHERE osm_id = ANY (SELECT osm_id FROM kindergarten_duplicates);

INSERT INTO kindergartens_polygons 
SELECT max(osm_id), 'polygon' AS origin_geometry, max(access) AS access, max(housenumber) AS housenumber, 
max(amenity) AS amenity, max(shop) AS shop, max(tags -> 'origin') AS origin, max(tags -> 'organic') AS organic, max(denomination) AS denomination,
max(brand) AS brand, max(name) AS name, max(operator) AS operator, max(public_transport) AS public_transport, max(railway) AS railway,
max(religion) AS religion, max(tags -> 'opening_hours') AS opening_hours, max(REF) AS ref, max(tags::TEXT)::hstore AS tags, null,
max(tags -> 'wheelchair') AS wheelchair, max(centroid)::geometry
FROM kindergarten_duplicates GROUP BY distance;

INSERT INTO pois 
SELECT DISTINCT p.osm_id,'point' as origin_geometry, p.access, "addr:housenumber" AS housenumber, p.amenity, p.shop, --p."addr:housenumber" doesn't work
p.tags -> 'origin' AS origin, p.tags -> 'organic' AS organic, p.denomination,p.brand,p.name,
p.operator,p.public_transport,p.railway,p.religion,p.tags -> 'opening_hours' as opening_hours, p.ref, p.tags::hstore AS tags, p.way as geom,
p.tags -> 'wheelchair' as wheelchair  
FROM planet_osm_point p, kindergartens_polygons kp 
WHERE p.amenity = 'kindergarten' EXCEPT 
SELECT DISTINCT kp.osm_id, kp.origin_geometry, kp.ACCESS, kp.housenumber, kp.amenity, kp.shop, kp.origin, kp.organic, kp.denomination, kp.brand, kp.name, 
kp.OPERATOR, kp.public_transport, kp.railway, kp.religion, kp.opening_hours, kp.REF, kp.tags, kp.geom, kp.wheelchair
FROM kindergartens_polygons kp, planet_osm_point p WHERE st_within(p.way, kp.geom) AND p.amenity = 'kindergarten'

UNION ALL 

SELECT kp.osm_id, kp.origin_geometry, kp.ACCESS, kp.housenumber, kp.amenity, kp.shop, kp.origin, kp.organic, kp.denomination, kp.brand, kp.name, 
kp.OPERATOR, kp.public_transport, kp.railway, kp.religion, kp.opening_hours, kp.REF, kp.tags, kp.centroid AS geom, kp.wheelchair
FROM kindergartens_polygons kp;

-- Insert outdoor fitness stations
/*
DROP TABLE IF EXISTS containing_polygons;
CREATE TEMP TABLE containing_polygons (geom geometry);

INSERT INTO containing_polygons
WITH merged_geom AS (
SELECT (ST_Dump(way)).geom AS geom
FROM (
	SELECT ST_Union(way) AS way		
	FROM planet_osm_polygon
	WHERE leisure = 'fitness_station') x)
SELECT m.geom FROM planet_osm_polygon pop, merged_geom m GROUP BY m.geom;

-- Paste zones attributes in containing polygons
DROP TABLE IF EXISTS grouping_polygons;
CREATE TEMP TABLE grouping_polygons  (LIKE planet_osm_polygon INCLUDING INDEXES);

INSERT INTO grouping_polygons
SELECT pop.* FROM containing_polygons
LEFT JOIN planet_osm_polygon pop 
ON ST_Contains(pop.way, geom)
WHERE pop.leisure = 'fitness_station';


INSERT INTO pois(

SELECT pop.osm_id, 'polygon' AS origin_geometry, pop.ACCESS AS ACCESS, pop."addr:housenumber" AS "addr:housenumber",
'outdoor_fitness_station' AS amenity, pop.shop AS store, pop.tags->'origin' AS origin, pop.tags->'organic' AS organic, pop.denomination AS denomination,
pop.brand AS brand, gp.name AS name, pop.OPERATOR AS operator, pop.public_transport AS public_transport, pop.railway AS railway,
pop.religion AS religion, pop.tags->'opening_hours' AS opening_hours, pop.ref AS ref, (pop.tags||hstore('sport', pop.sport)||hstore('leisure', pop.leisure))::hstore  AS tags, ST_Centroid(pop.way) AS geom, pop.tags ->'wheelchair' AS wheelchair
FROM planet_osm_polygon pop
LEFT JOIN grouping_polygons gp
ON ST_intersects(pop.way, gp.way)
WHERE pop.leisure = 'fitness_station' AND NOT ST_contains(pop.way, gp.way)

UNION ALL 

SELECT pop.osm_id, 'point' AS origin_geometry, pop.ACCESS AS ACCESS, pop."addr:housenumber" AS "addr:housenumber",
'outdoor_fitness_station' AS amenity, pop.shop AS store, pop.tags->'origin' AS origin, pop.tags->'organic' AS organic, pop.denomination AS denomination,
pop.brand AS brand, gp.name AS name, pop.OPERATOR AS operator, pop.public_transport AS public_transport, pop.railway AS railway,
pop.religion AS religion, pop.tags->'opening_hours' AS opening_hours, pop.ref AS ref, (pop.tags||hstore('sport', pop.sport)||hstore('leisure', pop.leisure))::hstore, pop.way AS geom, pop.tags ->'wheelchair' AS wheelchair
FROM planet_osm_point pop
LEFT JOIN grouping_polygons gp
ON ST_intersects(pop.way, gp.way)
WHERE pop.leisure = 'fitness_station' AND NOT ST_contains(pop.way, gp.way)
);

*/

--Distinguish kindergarten - nursery
SELECT pois_reclassification_array('name','kindergarten','amenity','nursery','left');
UPDATE pois p SET amenity = 'nursery'
WHERE amenity = 'kindergarten'	
AND (tags -> 'max_age') = '3';

/*End*/
------------------------------------------end kindergarten-------------------------------------------

--For Munich grocery == convencience

SELECT pois_reclassification('shop','grocery','amenity','convenience','singlevalue');
SELECT pois_reclassification('shop','fashion','amenity','clothes','singlevalue');

/*End*/

ALTER TABLE pois add column gid serial;
ALTER TABLE pois add primary key(gid); 
CREATE INDEX index_pois ON pois USING GIST (geom);
CREATE INDEX ON pois(amenity);

UPDATE pois SET amenity = shop
WHERE shop IS NOT NULL;
ALTER TABLE pois DROP COLUMN shop;

--Refinement Shopping

SELECT pois_reclassification_array('name','supermarket','amenity','discount_supermarket','any');
SELECT pois_reclassification_array('name','supermarket','amenity','hypermarket','any');
SELECT pois_reclassification_array('name','supermarket','amenity','no_end_consumer_store','any');
SELECT pois_reclassification_array('name','supermarket','amenity','health_food','any');

--Refinement Discount Gyms
SELECT pois_reclassification_array('name','gym','amenity','discount_gym','any');

UPDATE pois SET amenity = 'organic'
WHERE organic = 'only'
AND (amenity = 'supermarket' OR amenity = 'convenience');

UPDATE pois SET amenity = 'international_supermarket'
WHERE origin is not null
AND (amenity = 'supermarket' OR amenity = 'convenience');

/*End*/

--Select relevant operators bicycle_rental

DELETE FROM pois 
WHERE (NOT lower(operator) ~~ 
ANY
(
	SELECT concat('%',jsonb_object_keys(select_from_variable_container_o('pois_search_conditions')->'operators_bicycle_rental'),'%')
)  
OR operator IS NULL) 
AND amenity = 'bicycle_rental';


--INSERT public_transport_stops
WITH pt AS (
	SELECT osm_id,'bus_stop' as public_transport_stop,name,tags -> 'wheelchair' AS wheelchair, way as geom FROM planet_osm_point 
	WHERE highway = 'bus_stop' AND name IS NOT NULL
	UNION ALL
	SELECT osm_id,'bus_stop' as public_transport_stop,name,tags -> 'wheelchair' AS wheelchair, way as geom FROM planet_osm_point 
	WHERE public_transport = 'platform' AND highway <> 'bus_stop'
	AND name IS NOT NULL AND tags -> 'bus'='yes'
	UNION ALL
	SELECT osm_id,'tram_stop' as public_transport_stop,name,tags -> 'wheelchair' AS wheelchair,way as geom FROM planet_osm_point 
	WHERE public_transport = 'stop_position' 
	AND tags -> 'tram'='yes'
	AND name IS NOT NULL
	UNION ALL
	SELECT osm_id,'subway_entrance' as public_transport,name,tags -> 'wheelchair' AS wheelchair, way as geom FROM planet_osm_point
	WHERE railway = 'subway_entrance'
	UNION ALL
	SELECT osm_id,'rail_station' as public_transport,name,tags -> 'wheelchair' AS wheelchair,way as geom 
	FROM planet_osm_point WHERE railway = 'stop'
	AND tags -> 'train' ='yes'
)
INSERT INTO pois (osm_id,origin_geometry,amenity,name,wheelchair,geom) 
SELECT osm_id,'point',public_transport_stop,name,wheelchair,geom 
FROM pt;

DO $$                  
    BEGIN 
        IF EXISTS
            ( SELECT 1
              FROM   information_schema.tables 
              WHERE  table_schema = 'public'
              AND    table_name = 'pois_insert_no_fusion'
            )
        THEN
			INSERT INTO pois (origin_geometry,amenity,name,geom)
			SELECT 'point', amenity, name, geom 
			FROM pois_insert_no_fusion;
		END IF;
    END
$$ ;

WITH x AS (
	SELECT 'subway' as public_transport,name,way as geom  FROM planet_osm_point 
	WHERE public_transport ='station' 
	AND tags -> 'subway' = 'yes' AND railway <> 'proposed'
),
close_entrances AS (
	SELECT p.geom,x.name,min(st_distance(p.geom::geography,x.geom::geography))
	FROM pois p, x
	WHERE p.geom && ST_Buffer(x.geom::geography,500)::geometry
	GROUP BY p.geom,x.name
)
UPDATE pois p set name = c.name 
FROM close_entrances c
WHERE p.geom = c.geom
AND amenity = 'subway_entrance';

-- Multipoint for Sports center and waterparks

DROP TABLE IF EXISTS community_sports_center;
DROP TABLE IF EXISTS waterpark;
CREATE TABLE community_sports_center (LIKE planet_osm_polygon INCLUDING INDEXES);
INSERT INTO community_sports_center
SELECT * 
FROM planet_osm_polygon 
WHERE 
(
	(leisure = 'sports_centre' AND 
	lower(name) ~~ ANY (ARRAY(SELECT '%'||jsonb_array_elements_text(select_from_variable_container_o('pois_search_conditions') -> 'community_sport_centre') || '%')))
	OR 
	(landuse = 'recreation_ground' AND lower(name) ~~ ANY (ARRAY(SELECT '%'||jsonb_array_elements_text(select_from_variable_container_o('pois_search_conditions') -> 'community_sport_centre') || '%')
))
)
AND amenity IS NULL 
AND NOT (building IS NOT NULL AND sport IS null);

SELECT derive_access_from_polygons('community_sports_center','community_sports_center');
DROP TABLE IF EXISTS community_sports_center;

CREATE TABLE waterpark (LIKE planet_osm_polygon INCLUDING INDEXES);
INSERT INTO waterpark
SELECT * 
FROM planet_osm_polygon WHERE leisure = 'water_park' AND amenity IS NULL;
SELECT derive_access_from_polygons('waterpark','waterpark');
DROP TABLE IF EXISTS waterpark;

-- If custom_pois exists, run pois fusion 

DO $$                  
    BEGIN 
        IF EXISTS
            ( SELECT 1
              FROM   information_schema.tables 
              WHERE  table_schema = 'public'
              AND    table_name = 'custom_pois'
            )
        THEN
			--Run pois_fusion
			PERFORM pois_fusion();
        END IF ;
    END
$$ ;


--CREATE copy of pois for scenarios
DROP TABLE IF EXISTS pois_userinput;
CREATE TABLE pois_userinput (like pois INCLUDING ALL);
INSERT INTO pois_userinput
SELECT * FROM pois;

ALTER TABLE pois_userinput ADD COLUMN userid integer;
CREATE INDEX ON pois_userinput(userid);

--Add Foreign Key to pois_userinput 
ALTER TABLE pois_userinput ADD COLUMN pois_modified_id integer; 
ALTER TABLE pois_userinput
ADD CONSTRAINT pois_userinput_id_fkey FOREIGN KEY (pois_modified_id) 
REFERENCES pois_modified(id) ON DELETE CASCADE;