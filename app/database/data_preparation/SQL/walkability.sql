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

--Add columns for the walkability criteria
ALTER TABLE footpath_visualization ADD COLUMN IF NOT EXISTS sidewalk_quality int;
ALTER TABLE footpath_visualization ADD COLUMN IF NOT EXISTS traffic_protection int;
ALTER TABLE footpath_visualization ADD COLUMN IF NOT EXISTS security int;
ALTER TABLE footpath_visualization ADD COLUMN IF NOT EXISTS vegetation numeric;
ALTER TABLE footpath_visualization ADD COLUMN IF NOT EXISTS walking_environment int;
ALTER TABLE footpath_visualization ADD COLUMN IF NOT EXISTS comfort int;
ALTER TABLE footpath_visualization ADD COLUMN IF NOT EXISTS walkability int;

------------------------
--Calculate the values--
------------------------

----sidewalk quality----
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

----traffic protection----
--prepara data
DROP TABLE IF EXISTS highway_buffer;
CREATE TABLE highway_buffer as
SELECT ST_BUFFER(w.geom,0.00015) AS geom, lanes, maxspeed_forward
FROM ways w, study_area s 
WHERE highway IN ('living_street','residential','secondary','tertiary','primary')
AND ST_Intersects(w.geom,s.geom);

CREATE INDEX ON highway_buffer USING GIST(geom);

UPDATE footpath_visualization 
SET maxspeed_forward = NULL 
WHERE highway IN ('path','track');

UPDATE footpath_visualization 
SET maxspeed_forward = 5 
WHERE highway IN ('footway','pedestrian');

UPDATE footpath_visualization f SET lanes = h.lanes, maxspeed_forward = h.maxspeed_forward
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
DROP TABLE IF EXISTS crossings;
CREATE TEMP TABLE crossings (id serial, total_crossing int8);
INSERT INTO crossings
WITH buffer AS 
(
		SELECT id, st_buffer(geom::geography, 30) AS geom 
		FROM footpath_visualization
),
crossing AS 
(
	SELECT geom 
	FROM street_crossings 
	WHERE crossing IN ('zebra','traffic_signals')
)
SELECT b.id, count(crossing.geom) AS total_crossing
FROM buffer b
LEFT JOIN crossing ON st_contains(b.geom::geometry, crossing.geom)
GROUP BY b.id;

-- Assign info to footpaths
ALTER TABLE footpath_visualization DROP COLUMN IF EXISTS crossing;
ALTER TABLE footpath_visualization ADD COLUMN crossing int; 

UPDATE footpath_visualization 
SET crossing = -1
WHERE maxspeed_forward <= 30 OR maxspeed_forward IS NULL OR highway IN ('residential','service');

DROP TABLE crossings;


-- Noise (done in script footpaths_noise.sql)
--TODO: add accidents data as new column

--TODO: insert score for accidents

--calculate score
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


UPDATE footpath_visualization f SET walking_environment = 
round(100 * group_index(
	ARRAY[
		select_weight_walkability('landuse',landuse), 
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
	SELECT id, st_buffer(geom::geography, 30) AS geom FROM footpath_visualization),
bench AS (SELECT geom FROM street_furniture WHERE amenity = 'bench')
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
SET incline_percent = 0 WHERE incline_percent IS NULL; --TODO: add slope from DGM
--SELECT incline_percent, select_weight_walkability_range('slope',incline_percent) FROM footpath_visualization fu ORDER BY incline_percent DESC;

--- Waste-baskets
-- Create temp table to count waste baskets
DROP TABLE IF EXISTS waste_baskets;
CREATE TEMP TABLE waste_baskets (id serial, total_waste_basket int8);
INSERT INTO waste_baskets
WITH buffer AS (
	SELECT id, st_buffer(geom::geography, 20) AS geom FROM footpath_visualization),
waste_basket AS (SELECT geom FROM street_furniture WHERE amenity = 'waste_basket')
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
	SELECT id, st_buffer(geom::geography, 50) AS geom FROM footpath_visualization),
fountains AS (SELECT geom FROM street_furniture WHERE amenity IN ('fountain','drinking_water'))
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
	SELECT id, st_buffer(geom::geography, 300) AS geom FROM footpath_visualization),
toilets AS (SELECT geom FROM street_furniture WHERE amenity = 'toilets')
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
UPDATE footpath_visualization f SET comfort = round(10 * (2*bench + 3*waste_basket + 3*toilets + fountains),0);
UPDATE footpath_visualization f SET comfort = 100 WHERE street_furniture > 100;


----overall walkability----
UPDATE footpath_visualization f SET walkability = 
round((comfort*0.14) + (vegetation*0.14) + (security*0.14) + (traffic_protection*0.14) + (sidewalk_quality*0.29) + (walking_environment*0.14),0);
--TODO: enable calculation when one or more values are NULL 
--TODO: store number of columns without data

