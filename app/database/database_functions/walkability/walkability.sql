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
FROM '/opt/data//walkability.csv'
DELIMITER ','
CSV HEADER;
--Add columns for the walkability criteria
ALTER TABLE footpaths_union ADD COLUMN IF NOT EXISTS sidewalk_quality numeric;
ALTER TABLE footpaths_union ADD COLUMN IF NOT EXISTS traffic_protection numeric;
ALTER TABLE footpaths_union ADD COLUMN IF NOT EXISTS security numeric;
ALTER TABLE footpaths_union ADD COLUMN IF NOT EXISTS vegetation numeric;
ALTER TABLE footpaths_union ADD COLUMN IF NOT EXISTS walking_environment numeric;
ALTER TABLE footpaths_union ADD COLUMN IF NOT EXISTS comfort numeric;
ALTER TABLE footpaths_union ADD COLUMN IF NOT EXISTS walkability numeric;

------------------------
--Calculate the values--
------------------------


--sidewalk quality--
--prepara data
UPDATE footpaths_union f SET sidewalk = 'yes' where sidewalk is null and highway in ('footway', 'path', 'cycleway', 'living_street', 'steps', 'pedestrian');
UPDATE footpaths_union f SET sidewalk = 'no' where sidewalk is null;
UPDATE footpaths_union f SET smoothness = 'average' where smoothness is null;
UPDATE footpaths_union f SET smoothness = 'excellent' where smoothness = 'very_good';
UPDATE footpaths_union f SET surface = 'average' where surface is null;
UPDATE footpaths_union f SET width = 2.0 where width is null;

--calculate score
UPDATE footpaths_union f SET sidewalk_quality = 
(
    select_weight_walkability('sidewalk',sidewalk) 
	+ select_weight_walkability('smoothness',smoothness) 
	+ select_weight_walkability('surface',surface)
	+ select_weight_walkability('wheelchair',wheelchair_classified)
	+ select_weight_walkability_range('width', width)
)
*(100/0.29);

--traffic protection--
--prepara data
DROP TABLE IF EXISTS highway_buffer;
CREATE TABLE highway_buffer as
SELECT ST_BUFFER(geom,0.00015,'quad_segs=8') AS geom, lanes, oneway, maxspeed_forward, parking 
FROM ways 
WHERE highway IN ('living_street','residential','secondary','tertiary','primary');

UPDATE footpaths_union f SET lanes = 1 where lanes is null;
UPDATE footpaths_union f SET lanes = h.lanes
FROM highway_buffer h
WHERE ST_Within(f.geom,h.geom) and h.lanes is not null;

UPDATE footpaths_union f SET maxspeed_forward = 30 where highway in ('service','cycleway');
UPDATE footpaths_union f SET maxspeed_forward = 5 where highway in ('footpath','path','footway','track','steps','pedestrian');
UPDATE footpaths_union f SET maxspeed_forward = h.maxspeed_forward
FROM highway_buffer h
WHERE ST_Within(f.geom,h.geom) and h.maxspeed_forward is not null;

UPDATE footpaths_union f SET parking = 'lane' where (parking_lane_both is not null or parking_lane_left is not null OR parking_lane_right is not null);
UPDATE footpaths_union f SET parking = 'no' where parking is null;
UPDATE footpaths_union f SET parking = h.parking
FROM highway_buffer h
WHERE ST_Within(f.geom,h.geom) and h.parking is not null;


--calculate score
UPDATE footpaths_union f SET traffic_protection = 
(
    select_weight_walkability_range('lanes',lanes) 
	+ select_weight_walkability_range('maxspeed',maxspeed_forward)
	+ select_weight_walkability('parking',parking)
)
*(100/0.14);
--- Green index indicator
DROP TABLE IF EXISTS buffer_test;
CREATE TABLE buffer_test (id serial, geom geography);
INSERT INTO buffer_test
SELECT id, st_buffer(geom::geography, 8) AS geom FROM footpaths_union;

DROP TABLE IF EXISTS trees;
CREATE TABLE trees (id serial, trees numeric);

INSERT INTO trees
WITH trees AS (SELECT way FROM planet_osm_point WHERE "natural" = 'tree')
SELECT b.id, count(t.way) AS trees
FROM buffer_test b
LEFT JOIN trees t ON st_contains(b.geom::geometry, t.way)
GROUP BY b.id;

--- Alter table
ALTER TABLE footpaths_union DROP COLUMN IF EXISTS trees;
ALTER TABLE footpaths_union ADD COLUMN trees varchar; 
UPDATE footpaths_union 
SET trees = 'yes' 
FROM trees t
WHERE t.id = footpaths_union.id AND t.trees >= 1;
UPDATE footpaths_union 
SET trees = 'no'
FROM trees t
WHERE t.id = footpaths_union.id AND t.trees = 0;
SELECT * FROM footpaths_union fu;

DROP TABLE IF EXISTS green_landuse;
CREATE TABLE green_landuse (id serial, score numeric);
INSERT INTO green_landuse
WITH landuses AS (
	SELECT * FROM landuse_osm lo WHERE landuse = ANY (array['greenfield','farmland','green','grass'])),
touching_landuse AS (
SELECT b.id, l.landuse AS landuse
FROM buffer_test b
LEFT JOIN landuses l ON st_intersects(b.geom::geometry, l.geom)
GROUP BY b.id, l.landuse)
SELECT id, count(landuse) FROM touching_landuse GROUP BY id ORDER BY id;

ALTER TABLE footpaths_union DROP COLUMN IF EXISTS green_landuse ;
ALTER TABLE footpaths_union ADD COLUMN green_landuse varchar;
UPDATE footpaths_union 
SET green_landuse = 'yes' 
FROM green_landuse gl
WHERE gl.id = footpaths_union.id AND gl.score >= 1;
UPDATE footpaths_union 
SET green_landuse = 'no'
FROM green_landuse gl
WHERE gl.id = footpaths_union.id AND gl.score = 0;

UPDATE footpaths_union f SET vegetation = 
(
    (select_weight_walkability('vegetation',trees)::NUMERIC)*0.3 +
    (select_weight_walkability('vegetation',green_landuse)::NUMERIC)*0.7
)
*(100/0.14);
--- Attractiveness indicators
--Landuse
DROP TABLE IF EXISTS buffer_test;
CREATE TEMP TABLE buffer_test (id serial, geom geography);
INSERT INTO buffer_test
SELECT id, st_buffer(geom::geography, 8) AS geom FROM footpaths_union;

DROP TABLE IF EXISTS lu_score;
CREATE TABLE lu_score (id serial, score numeric);
INSERT INTO lu_score
WITH landuses AS (SELECT * FROM landuse_osm lo WHERE landuse = ANY (SELECT sring_condition FROM walkability WHERE attribute = 'land_use')),
unique_landuse AS (SELECT DISTINCT b.id, l.landuse AS landuse
	FROM buffer_test b
	LEFT JOIN landuses l ON st_intersects(b.geom::geometry, l.geom)),
lu_link AS (SELECT id, count(id) FROM unique_landuse GROUP BY id),
max_landuses AS (SELECT max(count) AS max_lu FROM lu_link)
SELECT id, ((count::numeric/(SELECT* FROM max_landuses)::NUMERIC)*0.14) AS score FROM lu_link;

ALTER TABLE footpaths_union DROP COLUMN IF EXISTS landuse_score;
ALTER TABLE footpaths_union ADD COLUMN landuse_score NUMERIC;
UPDATE footpaths_union SET landuse_score = score
FROM lu_score
WHERE lu_score.id = footpaths_union.id;

UPDATE footpaths_union f 
SET walking_environment = landuse_score*(100/0.14);

ALTER TABLE footpaths_union DROP COLUMN IF EXISTS landuse_score;
-- POIS along the route
-- Pop density
--- Comfort indicators
-- Benches

DROP TABLE IF EXISTS benches;
CREATE TEMP TABLE benches (id serial, total_bench int8);
INSERT INTO benches
WITH buffer AS (
	SELECT id, length_m,  st_buffer(geom::geography, 8) AS geom FROM footpaths_union),
bench AS (SELECT geom FROM pois WHERE amenity = 'bench')
SELECT b.id, count(bench.geom) AS total_bench
FROM buffer b
LEFT JOIN bench ON st_contains(b.geom::geometry, bench.geom)
GROUP BY b.id;

-- Tag yes or no for function
ALTER TABLE footpaths_union DROP COLUMN IF EXISTS bench;
ALTER TABLE footpaths_union ADD COLUMN bench varchar; 
UPDATE footpaths_union 
SET bench = 'yes' 
FROM benches
WHERE benches.id = footpaths_union.id AND benches.total_bench >= 1;
UPDATE footpaths_union 
SET bench = 'no'
FROM benches 
WHERE benches.id = footpaths_union.id AND benches.total_bench = 0;

-- Slope

UPDATE footpaths_union 
SET incline_percent = 0 WHERE incline_percent IS NULL;
--SELECT incline_percent, select_weight_walkability_range('slope',incline_percent) FROM footpaths_union fu ORDER BY incline_percent DESC;

--- Furniture
-- Define general buffer for next point-based measures1
DROP TABLE IF EXISTS buffer_footpaths;
CREATE TABLE buffer_footpaths (id serial, geom geography);

INSERT INTO buffer_footpaths
SELECT id, st_buffer(geom::geography, 8) AS geom FROM footpaths_union;

DROP TABLE IF EXISTS furniture;
CREATE TEMP TABLE furniture(id serial, total_furniture int8);

INSERT INTO furniture
WITH furniture AS (SELECT geom FROM pois WHERE amenity = 'waste_basket')
SELECT b.id, count(f.geom) AS furniture
FROM buffer_footpaths b
LEFT JOIN furniture f ON st_contains(b.geom::geometry, f.geom)
GROUP BY b.id;

ALTER TABLE footpaths_union DROP COLUMN IF EXISTS furniture;
ALTER TABLE footpaths_union ADD COLUMN furniture varchar; 
UPDATE footpaths_union 
SET furniture = 'yes' 
FROM furniture f
WHERE f.id = footpaths_union.id AND f.total_furniture >= 1;
UPDATE footpaths_union 
SET furniture = 'no'
FROM furniture f
WHERE f.id = footpaths_union.id AND f.total_furniture = 0;

--- Bathrooms
DROP TABLE IF EXISTS toilet;
CREATE TEMP TABLE toilet(id serial, total_toilet int8);

INSERT INTO toilet
WITH toilet AS (SELECT geom FROM pois WHERE amenity = 'toilets')
SELECT b.id, count(t.geom) AS toilet
FROM buffer_footpaths b
LEFT JOIN toilet t ON st_contains(b.geom::geometry, t.geom)
GROUP BY b.id;

ALTER TABLE footpaths_union DROP COLUMN IF EXISTS toilet;
ALTER TABLE footpaths_union ADD COLUMN toilet varchar; 
UPDATE footpaths_union 
SET toilet = 'yes' 
FROM toilet t
WHERE t.id = footpaths_union.id AND t.total_toilet >= 1;
UPDATE footpaths_union 
SET toilet = 'no'
FROM toilet t
WHERE t.id = footpaths_union.id AND t.total_toilet = 0;

--- Drinking fountains
DROP TABLE IF EXISTS drinking;
CREATE TEMP TABLE drinking(id serial, total_drinking int8);

INSERT INTO drinking
WITH drinking AS (SELECT geom FROM pois WHERE amenity = 'drinking_water')
SELECT b.id, count(d.geom) AS total_drinking
FROM buffer_footpaths b
LEFT JOIN drinking d ON st_contains(b.geom::geometry, d.geom)
GROUP BY b.id;

ALTER TABLE footpaths_union DROP COLUMN IF EXISTS drinking;
ALTER TABLE footpaths_union ADD COLUMN drinking varchar; 
UPDATE footpaths_union 
SET drinking = 'yes' 
FROM drinking d
WHERE d.id = footpaths_union.id AND d.total_drinking >= 1;
UPDATE footpaths_union 
SET drinking = 'no'
FROM drinking d
WHERE d.id = footpaths_union.id AND d.total_drinking = 0;

--- Street marking or traffic light
DROP TABLE IF EXISTS marking;
CREATE TEMP TABLE marking(id serial, total_marking int8);

INSERT INTO marking
WITH marking AS (SELECT geom FROM street_crossings WHERE highway = 'crossing' AND crossing = ANY (ARRAY ['marked','traffic_signals']))
SELECT b.id, count(m.geom) AS total_marking
FROM buffer_footpaths b
LEFT JOIN marking m ON st_contains(b.geom::geometry, m.geom)
GROUP BY b.id;

ALTER TABLE footpaths_union DROP COLUMN IF EXISTS marking;
ALTER TABLE footpaths_union ADD COLUMN marking varchar; 

UPDATE footpaths_union 
SET marking = 'yes' 
FROM marking m
WHERE m.id = footpaths_union.id AND m.total_marking >= 1;
UPDATE footpaths_union 
SET marking = 'no'
FROM marking m
WHERE m.id = footpaths_union.id AND m.total_marking = 0;

--- Compile in the footpaths union table 
UPDATE footpaths_union f SET comfort = 
(
    select_weight_walkability('equipment',bench) +
    select_weight_walkability('toilets',toilet) +
    select_weight_walkability('drinking_fountain',drinking) +
    select_weight_walkability('cross_mark',marking) +
    select_weight_walkability_range('slope', incline_percent)
)
*(100/0.14);

ALTER TABLE footpaths_union DROP COLUMN IF EXISTS bench;
ALTER TABLE footpaths_union DROP COLUMN IF EXISTS furniture;
ALTER TABLE footpaths_union DROP COLUMN IF EXISTS toilet;
ALTER TABLE footpaths_union DROP COLUMN IF EXISTS drinking;
ALTER TABLE footpaths_union DROP COLUMN IF EXISTS marking;
ALTER TABLE footpaths_union DROP COLUMN IF EXISTS trees;
ALTER TABLE footpaths_union DROP COLUMN IF EXISTS green_landuse;
