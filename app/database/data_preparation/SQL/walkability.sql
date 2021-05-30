--THIS FILE NEEDS TO BE EXECUTED TO COMPUTE THE WALKBILITY INDICES

-- Load walkability table 
DROP TABLE IF EXISTS walkability;
CREATE TABLE walkability(
	category varchar,
	criteria varchar,
	attribute varchar,
	sring_condition varchar,
	min_value numeric,
	max_value numeric,
	value numeric,
	weight numeric
);

COPY walkability
FROM '/opt/data_preparation//walkability.csv'
DELIMITER ';'
CSV HEADER;

ALTER TABLE walkability ADD COLUMN gid serial;
ALTER TABLE walkability ADD PRIMARY KEY(gid);

----##########################################################################################################################----
----########################################################SIDEWALK QUALITY##################################################----
----##########################################################################################################################----
--prepara data
UPDATE footpath_visualization f 
SET sidewalk = 'yes' 
WHERE sidewalk IS NULL 
AND highway in ('footway', 'path', 'cycleway', 'living_street', 'steps', 'pedestrian', 'track');

UPDATE footpath_visualization f 
SET surface = 'asphalt' 
WHERE surface IS NULL 
AND highway IN ('residential','tertiary','secondary','primary','living_street');

UPDATE footpath_visualization f 
SET surface = NULL 
WHERE surface NOT IN ('paved','asphalt','concrete','concrete:lanes','paving_stones','cobblestone:flattened','stone','sandstone','sett','metal','unhewn_cobblestone','cobblestone','unpaved','compacted','fine_gravel','metal_grid','gravel','pebblestone','rock','wood','ground','dirt','earth','grass','grass_paver','mud','sand');

--calculate score
UPDATE footpath_visualization f SET sidewalk_quality = 
round(100 * group_index(
	ARRAY[
		select_weight_walkability('sidewalk',sidewalk), 
		select_weight_walkability('smoothness',smoothness),
		select_weight_walkability('surface',surface),
		select_weight_walkability('wheelchair',wheelchair_classified),
		select_weight_walkability_range('width', width)
	],
	ARRAY[
		select_full_weight_walkability('sidewalk'),
		select_full_weight_walkability('smoothness'),
		select_full_weight_walkability('surface'),
		select_full_weight_walkability('wheelchair'),
		select_full_weight_walkability('width')
	]
),0);

----##########################################################################################################################----
----#######################################################TRAFFIC PROTECTION#################################################----
----##########################################################################################################################----
--prepara data
DROP TABLE IF EXISTS highway_buffer;
CREATE TABLE highway_buffer as
SELECT ST_BUFFER(w.geom,0.00015) AS geom, lanes, maxspeed_forward
FROM ways w, study_area s 
WHERE highway IN ('living_street','residential','secondary','tertiary','primary')
AND ST_Intersects(w.geom,s.geom);

CREATE INDEX ON highway_buffer USING GIST(geom);

UPDATE footpath_visualization 
SET maxspeed = NULL 
WHERE highway IN ('path','track');

UPDATE footpath_visualization 
SET maxspeed = 5 
WHERE highway IN ('footway','pedestrian');

UPDATE footpath_visualization f SET lanes = h.lanes, maxspeed = h.maxspeed_forward
FROM 
(
	SELECT f.id, f.geom, h.lanes, h.maxspeed_forward, MAX(ST_LENGTH(ST_INTERSECTION(h.geom, f.geom))/ST_LENGTH(f.geom)) AS share_intersection
	FROM highway_buffer h, footpath_visualization f 
	WHERE ST_Intersects(h.geom,f.geom)
	AND st_geometrytype(ST_INTERSECTION(h.geom, f.geom)) = 'ST_LineString'
	AND ST_LENGTH(ST_INTERSECTION(h.geom, f.geom))/ST_LENGTH(f.geom) > 0.2
	GROUP BY f.id, h.geom, h.lanes, h.maxspeed_forward
) h
WHERE h.id = f.id;

UPDATE footpath_visualization f SET parking = 'yes'
FROM 
(
	SELECT f.id 
	FROM parking p, footpath_visualization f, study_area s
	WHERE ST_Intersects(f.geom,s.geom) 
	AND ST_intersects(ST_Buffer(p.geom,0.00015),f.geom)
	AND st_geometrytype(ST_INTERSECTION(ST_Buffer(p.geom,0.00015), f.geom)) = 'ST_LineString'
	AND ST_LENGTH(ST_INTERSECTION(ST_Buffer(p.geom,0.00015), f.geom))/ST_LENGTH(f.geom) > 0.5
	AND p.parking_lane IS NOT NULL 
	AND p.parking_lane <> 'no'
) p 
WHERE f.id = p.id;

--street crossings
-- Create temp table to count street crossings
DROP TABLE IF EXISTS relevant_crossings;
CREATE TEMP TABLE relevant_crossings AS 
SELECT geom 
FROM street_crossings 
WHERE crossing IN ('zebra','traffic_signals'); 

CREATE INDEX ON relevant_crossings USING GIST(geom);

/*Assing number of crossing to footpath_visualization*/
ALTER TABLE footpath_visualization DROP COLUMN IF EXISTS cnt_crossings;
ALTER TABLE footpath_visualization ADD COLUMN cnt_crossings int; 
WITH cnt_table AS 
(
	SELECT id, COALESCE(points_sum) AS points_sum 
	FROM footpaths_get_points_sum('pois', 30)
)
UPDATE footpath_visualization f
SET cnt_crossings = points_sum 
FROM cnt_table c
WHERE f.id = c.id;

/*Label footpaths that are not affected by crossings*/
UPDATE footpath_visualization 
SET cnt_crossings = -1
WHERE maxspeed <= 30 
OR maxspeed IS NULL OR highway IN ('residential','service');

/*For each footpath noise levels (day and night) are derived an aggregated for different sound sources*/
DO $$     
	DECLARE 
		noise_key TEXT;
    BEGIN     

		IF EXISTS ( 	
			SELECT 1
            FROM   information_schema.tables 
            WHERE  table_schema = 'public'
            AND    table_name = 'noise'
        ) 
		THEN 
		
			DROP TABLE IF EXISTS noise_levels_footpaths;
			CREATE TEMP TABLE noise_levels_footpaths 
			(
			gid serial, 
			footpath_id integer, 
			noise_level_db integer, 
			noise_type text,
			CONSTRAINT noise_levels_footpaths_pkey PRIMARY KEY (gid)
			);

			FOR noise_key IN SELECT DISTINCT noise_type FROM noise  	
			LOOP
				RAISE NOTICE 'Following noise type will be calculated: %', noise_key;
				DROP TABLE IF EXISTS noise_subdivide;
				CREATE TEMP TABLE noise_subdivide AS 
				SELECT ST_SUBDIVIDE((ST_DUMP(geom)).geom, 50) AS geom, noise_level_db  
				FROM noise fn 
				WHERE noise_type = noise_key;
				
				ALTER TABLE noise_subdivide ADD COLUMN gid serial;
				ALTER TABLE noise_subdivide ADD PRIMARY KEY(gid);
				CREATE INDEX ON noise_subdivide USING GIST(geom);
				
				INSERT INTO noise_levels_footpaths(footpath_id,noise_level_db,noise_type)
				SELECT id, 
				COALESCE(arr_polygon_attr[array_position(arr_shares, array_greatest(arr_shares))]::integer, 0) AS val, noise_key
				FROM footpaths_get_polygon_attr('noise_subdivide','noise_level_db');
				
			END LOOP;
		END IF; 
    END
$$ ;

WITH noise_day AS 
(
	SELECT footpath_id, (10 * LOG(SUM(power(10,(noise_level_db::float/10))))) AS noise 
	FROM noise_levels_footpaths
	WHERE noise_type LIKE '%day%'
	GROUP BY footpath_id
)
UPDATE footpath_visualization f
SET noise_day = n.noise 
FROM noise_day n  
WHERE f.id = n.footpath_id; 

WITH noise_night AS 
(
	SELECT footpath_id, (10 * LOG(SUM(power(10,(noise_level_db::float/10))))) AS noise 
	FROM noise_levels_footpaths
	WHERE noise_type LIKE '%night%'
	GROUP BY footpath_id
)
UPDATE footpath_visualization f
SET noise_night = n.noise 
FROM noise_night n  
WHERE f.id = n.footpath_id; 

/*Count Accidents*/
/*Assing number of crossing to footpath_visualization*/
DROP TABLE IF EXISTS accidents_foot; 
CREATE TABLE accidents_foot AS 
SELECT geom 
FROM accidents 
WHERE istfuss = '1'; 

CREATE INDEX ON accidents_foot USING GIST(geom);

WITH cnt_table AS 
(
	SELECT f.id, COALESCE(points_sum,0) AS points_sum 
	FROM footpath_visualization f 
	LEFT JOIN footpaths_get_points_sum('accidents_foot', 30) c
	ON f.id = c.id 	
)
UPDATE footpath_visualization f
SET cnt_accidents = points_sum 
FROM cnt_table c
WHERE f.id = c.id;

----##########################################################################################################################----
----#############################################################SAFETY#######################################################----
----##########################################################################################################################----
WITH variables AS 
(
    SELECT select_from_variable_container_o('lit') AS lit
)
UPDATE footpath_visualization f SET lit_classified = x.lit_classified
FROM
    (SELECT f.id,
    CASE WHEN 
        lit IN ('yes','Yes','automatic','24/7','sunset-sunrise') 
        OR (lit IS NULL AND highway IN (SELECT jsonb_array_elements_text((lit ->> 'highway_yes')::jsonb) FROM variables)
			AND maxspeed<80)
        THEN 'yes' 
    WHEN
        lit IN ('no','No','disused')
        OR (lit IS NULL AND (highway IN (SELECT jsonb_array_elements_text((lit ->> 'highway_no')::jsonb) FROM variables) 
        OR surface IN (SELECT jsonb_array_elements_text((lit ->> 'surface_no')::jsonb) FROM variables)
		OR maxspeed>=80)
        )
        THEN 'no'
    ELSE 'unclassified'
    END AS lit_classified 
    FROM footpath_visualization f
    ) x
WHERE f.id = x.id;

--Precalculation of visualized features for lit
DROP TABLE IF EXISTS buffer_lamps;
CREATE TABLE buffer_lamps as
SELECT ST_SUBDIVIDE((ST_DUMP(ST_UNION(ST_BUFFER(geom,15 * meter_degree())))).geom, 100) AS geom, 'yes' AS lit 
FROM street_furniture
WHERE amenity = 'street_lamp';

CREATE INDEX ON buffer_lamps USING gist(geom);

DROP TABLE IF EXISTS footpaths_lit; 
CREATE TEMP TABLE footpaths_lit AS 
SELECT DISTINCT id 
FROM footpaths_get_polygon_attr('buffer_lamps','lit')
WHERE arr_shares IS NOT NULL 
AND arr_polygon_attr = ARRAY['yes']
AND arr_shares[1] > 0.3; 

UPDATE footpath_visualization f  
SET lit_classified = 'yes'
FROM footpaths_lit l 
WHERE f.id = l.id;


UPDATE footpath_visualization f SET traffic_protection = 
round(100 * group_index(
	ARRAY[
		select_weight_walkability_range('lanes',lanes),
		select_weight_walkability_range('maxspeed',maxspeed_forward),
		select_weight_walkability_range('crossing',crossing),
		select_weight_walkability('parking',parking),
		select_weight_walkability_range('noise',noise)
	],
	ARRAY[
		select_full_weight_walkability('lanes'),
		select_full_weight_walkability('maxspeed'),
		select_full_weight_walkability('crossing'),
		select_full_weight_walkability('parking'),
		select_full_weight_walkability('noise')
	]
),0);

UPDATE footpath_visualization SET traffic_protection = 100
WHERE traffic_protection IS NULL; 

----security----
UPDATE footpath_visualization f SET security = 
round(100 * group_index(
	ARRAY[
		select_weight_walkability('lit_classified',lit_classified)
	],
	ARRAY[
		select_full_weight_walkability('lit_classified')
	]
),0);




--UPDATE footpath_visualization f SET security = 50 WHERE security IS NULL;

/*
--- Green index indicator
DROP TABLE IF EXISTS buffer_test;
CREATE TABLE buffer_test (id serial, geom geography);
INSERT INTO buffer_test
SELECT id, st_buffer(geom::geography, 8) AS geom FROM footpath_visualization;

DROP TABLE IF EXISTS trees;
CREATE TABLE trees (id serial, trees numeric);

INSERT INTO trees
WITH trees AS 
(
	SELECT way FROM planet_osm_point WHERE "natural" = 'tree'
)
SELECT b.id, count(t.way) AS trees
FROM buffer_test b
LEFT JOIN trees t ON st_contains(b.geom::geometry, t.way)
GROUP BY b.id;

--- Alter table
ALTER TABLE footpath_visualization DROP COLUMN IF EXISTS trees;
ALTER TABLE footpath_visualization ADD COLUMN trees varchar; 
UPDATE footpath_visualization 
SET trees = 'yes' 
FROM trees t
WHERE t.id = footpath_visualization.id AND t.trees >= 1;
UPDATE footpath_visualization 
SET trees = 'no'
FROM trees t
WHERE t.id = footpath_visualization.id AND t.trees = 0;
SELECT * FROM footpath_visualization fu;
*/
WITH green_share AS 
(
	SELECT f.id, ST_length(ST_Intersection(a.geom, f.geom))/ST_LENGTH(f.geom) AS green_share
	FROM footpath_visualization f, aois a, study_area s 
	WHERE ST_Intersects(f.geom, a.geom)
	AND ST_Intersects(s.geom,a.geom)
	AND st_geometrytype(ST_Intersection(a.geom, f.geom)) = 'ST_LineString' 
)
UPDATE footpath_visualization f SET vegetation = 
(
    (select_weight_walkability_range('vegetation',g.green_share::numeric)::NUMERIC)
)*(100/0.14)
FROM green_share g
WHERE f.id = g.id;

UPDATE footpath_visualization 
SET vegetation = 0 
WHERE vegetation IS NULL; 

--- Attractiveness of walking environment indicators
-- TODO: Pop density (issue #986) -> in layer_preparation

----##########################################################################################################################----
----#####################################################WALKING ENVIRONMENT##################################################----
----##########################################################################################################################----

----------------------
---Add landuse data---
----------------------
--clean landuse ##copy this query to the "buildings_residential.sql" script when finished
DROP TABLE IF EXISTS inner_polygons;
CREATE TABLE inner_polygons AS
SELECT lo.*
FROM landuse_osm l 
JOIN landuse_osm lo ON (ST_Contains(l.geom, lo.geom)) WHERE l.gid != lo.gid;

UPDATE landuse_osm l
SET geom = st_difference(l.geom, i.geom)
FROM inner_polygons i
WHERE l.gid=i.gid;

INSERT INTO landuse_osm 
SELECT * FROM inner_polygons; 
--TODO: maybe insert a loop (for polygons inside the inner_polygons)

DROP TABLE inner_polygons;

--assign info about landuse to footpath_visualization
ALTER TABLE footpath_visualization ADD COLUMN IF NOT EXISTS landuse text;

UPDATE footpath_visualization f  
SET landuse = ARRAY[l.landuse_simplified]
FROM landuse_osm l
WHERE ST_CONTAINS(l.geom,f.geom);

DROP TABLE IF EXISTS footpath_ids_landuse;
CREATE TABLE footpath_ids_landuse AS --TODO: use buffer and intersect with area 
WITH i AS 
(
    SELECT f.id, f.geom, ST_LENGTH(ST_Intersection(l.geom, f.geom)) len_intersection, l.landuse_simplified AS landuse
    FROM  landuse_osm l, footpath_visualization f
    WHERE ST_Intersects(f.geom, l.geom)  
    AND f.landuse IS NULL
    AND l.landuse_simplified IS NOT NULL
)   
SELECT id, get_attr_for_max_val(array_agg((len_intersection * 1000000000)::integer), array_agg(landuse)) AS landuse 
FROM i
GROUP BY id; 

ALTER TABLE footpath_ids_landuse ADD PRIMARY KEY(id); 

UPDATE footpath_visualization f  
SET landuse = ARRAY[l.landuse] 
FROM footpath_ids_landuse l 
WHERE f.id = l.id; 
DROP TABLE footpath_ids_landuse;

--assign info about population density
--TODO: assign "high","medium","low","no" accoridng to buffer -> intersection with pop.

--Classify by number of POIs
CREATE TEMP TABLE pois_to_count AS 
SELECT geom 
FROM pois 
WHERE amenity NOT IN ('parking','bench','information','parking_space','waste_basket','fountain','toilets','carging_station','bicycle_parking','parking_entrance','motorcycle_parking','hunting_stand');

CREATE INDEX ON pois_to_count USING GIST(geom);

WITH cnt_table AS 
(
	SELECT f.id, COALESCE(points_sum,0) AS points_sum, f.geom  
	FROM footpath_visualization f 
	LEFT JOIN footpaths_get_points_sum('pois_to_count', 50) c
	ON f.id = c.id 	
), 
classify AS 
(
	SELECT c.id, sring_condition 
	FROM walkability w, cnt_table c 
	WHERE attribute = 'pois'
	AND (w.min_value < c.points_sum OR w.min_value IS NULL)  
	AND (w.max_value > c.points_sum OR w.max_value IS NULL)
)
UPDATE footpath_visualization f
SET pois = c.sring_condition 
FROM classify c
WHERE f.id = c.id;

--Classify by number of Population
WITH cnt_table AS 
(
	SELECT id, points_sum
	FROM footpaths_get_points_sum('population', 50, 'population') c
),
percentiles AS 
(
	SELECT id, points_sum, ntile(4) over (order by points_sum) AS percentile
	FROM cnt_table 
	WHERE points_sum <> 0 
	AND points_sum IS NOT NULL 
),
combined AS 
(
	SELECT f.id, (COALESCE(p.percentile,0) + 1) AS arr_index 
	FROM footpath_visualization f 
	LEFT JOIN percentiles p 
	ON f.id = p.id 
)
UPDATE footpath_visualization f
SET population = (ARRAY['no','very_low','low','medium','high','very_high'])[arr_index] 
FROM combined c 
WHERE f.id = c.id; 

UPDATE footpath_visualization f SET walking_environment = 
round(100 * group_index(
	ARRAY[
		select_weight_walkability('landuse',landuse[1]), 
		select_weight_walkability('population',population),
		select_weight_walkability('pois',pois)
	],
	ARRAY[
		select_full_weight_walkability('landuse'),
		select_full_weight_walkability('population'),
		select_full_weight_walkability('pois')
	]
),0);


----Comfort----
-- Benches
-- Create temp table to count benches
DROP TABLE IF EXISTS benches;
CREATE TEMP TABLE benches (id serial, total_bench int8);
INSERT INTO benches
WITH buffer AS (
	SELECT id, st_buffer(geom::geography, 30) AS geom FROM footpath_visualization
),
bench AS 
(
	SELECT geom FROM street_furniture WHERE amenity = 'bench'
)
SELECT b.id, count(bench.geom) AS total_bench
FROM buffer b
LEFT JOIN bench ON st_contains(b.geom::geometry, bench.geom)
GROUP BY b.id;

-- Assign info to footpaths
ALTER TABLE footpath_visualization DROP COLUMN IF EXISTS bench;
ALTER TABLE footpath_visualization ADD COLUMN bench int; 

UPDATE footpath_visualization 
SET bench = benches.total_bench
FROM benches
WHERE benches.id = footpath_visualization.id;

DROP TABLE benches;

-- Slope

UPDATE footpath_visualization 
SET incline_percent = 0 
WHERE incline_percent IS NULL; --TODO: add slope from DGM
--SELECT incline_percent, select_weight_walkability_range('slope',incline_percent) FROM footpath_visualization fu ORDER BY incline_percent DESC;

--- Waste-baskets
-- Create temp table to count waste baskets
DROP TABLE IF EXISTS waste_baskets;
CREATE TEMP TABLE waste_baskets (id serial, total_waste_basket int8);
INSERT INTO waste_baskets
WITH buffer AS (
	SELECT id, st_buffer(geom::geography, 20) AS geom 
	FROM footpath_visualization
),
waste_basket AS (
	SELECT geom 
	FROM street_furniture 
	WHERE amenity = 'waste_basket'
)
SELECT b.id, count(waste_basket.geom) AS total_waste_basket
FROM buffer b
LEFT JOIN waste_basket ON st_contains(b.geom::geometry, waste_basket.geom)
GROUP BY b.id;

-- Assign info to footpaths
ALTER TABLE footpath_visualization DROP COLUMN IF EXISTS waste_basket;
ALTER TABLE footpath_visualization ADD COLUMN waste_basket int; 

UPDATE footpath_visualization 
SET waste_basket = waste_baskets.total_waste_basket
FROM waste_baskets
WHERE waste_baskets.id = footpath_visualization.id;

DROP TABLE waste_baskets;

--- Fountains
-- Create temp table to count fountains
DROP TABLE IF EXISTS fountains;
CREATE TEMP TABLE fountains (id serial, total_fountains int8);
INSERT INTO fountains
WITH buffer AS (
	SELECT id, st_buffer(geom::geography, 50) AS geom 
	FROM footpath_visualization
),
fountains AS (
	SELECT geom 
	FROM street_furniture 
	WHERE amenity IN ('fountain','drinking_water')
)
SELECT b.id, count(fountains.geom) AS total_fountains
FROM buffer b
LEFT JOIN fountains ON st_contains(b.geom::geometry, fountains.geom)
GROUP BY b.id;

-- Assign info to footpaths
ALTER TABLE footpath_visualization DROP COLUMN IF EXISTS fountains;
ALTER TABLE footpath_visualization ADD COLUMN fountains int; 

UPDATE footpath_visualization 
SET fountains = fountains.total_fountains
FROM fountains
WHERE fountains.id = footpath_visualization.id;

DROP TABLE fountains;

--- Bathrooms
-- Create temp table to count public toilets
DROP TABLE IF EXISTS toilets;
CREATE TEMP TABLE toilets (id serial, total_toilets int8);
INSERT INTO toilets
WITH buffer AS (
	SELECT id, st_buffer(geom::geography, 300) AS geom 
	FROM footpath_visualization
),
toilets AS (
	SELECT geom 
	FROM street_furniture 
	WHERE amenity = 'toilets'
)
SELECT b.id, count(toilets.geom) AS total_toilets
FROM buffer b
LEFT JOIN toilets ON st_contains(b.geom::geometry, toilets.geom)
GROUP BY b.id;

-- Assign info to footpaths
ALTER TABLE footpath_visualization DROP COLUMN IF EXISTS toilets;
ALTER TABLE footpath_visualization ADD COLUMN toilets int; 

UPDATE footpath_visualization 
SET toilets = toilets.total_toilets
FROM toilets
WHERE toilets.id = footpath_visualization.id;

DROP TABLE toilets;

--- Street furniture sum
ALTER TABLE footpath_visualization DROP COLUMN street_furniture;
ALTER TABLE footpath_visualization ADD COLUMN IF NOT EXISTS street_furniture int;

UPDATE footpath_visualization f 
SET comfort = round(10 * (2*bench + 3*waste_basket + 3*toilets + fountains),0);

UPDATE footpath_visualization f 
SET comfort = 100 WHERE street_furniture > 100;


----overall walkability----
UPDATE footpath_visualization f SET walkability = 
round((comfort*0.14) + (vegetation*0.14) + (security*0.14) + (traffic_protection*0.14) + (sidewalk_quality*0.29) + (walking_environment*0.14),0);
--TODO: enable calculation when one or more values are NULL 

UPDATE footpath_visualization f SET data_quality = (22-num_nulls(width,maxspeed,incline_percent,lanes,noise_day,noise_night,
lit_classified,parking,sidewalk,smoothness,surface,wheelchair_classified,cnt_crossings,cnt_accidents,cnt_benches,
cnt_waste_baskets,cnt_fountains,cnt_toilets,population,pois,landuse,street_furniture))::float/22.0;

