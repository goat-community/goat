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
ALTER TABLE footpath_visualization ADD COLUMN IF NOT EXISTS sidewalk_quality numeric;
ALTER TABLE footpath_visualization ADD COLUMN IF NOT EXISTS traffic_protection numeric;
ALTER TABLE footpath_visualization ADD COLUMN IF NOT EXISTS security numeric;
ALTER TABLE footpath_visualization ADD COLUMN IF NOT EXISTS vegetation numeric;
ALTER TABLE footpath_visualization ADD COLUMN IF NOT EXISTS walking_environment numeric;
ALTER TABLE footpath_visualization ADD COLUMN IF NOT EXISTS comfort numeric;
ALTER TABLE footpath_visualization ADD COLUMN IF NOT EXISTS walkability numeric;

------------------------
--Calculate the values--
------------------------


--sidewalk quality--
--prepara data
UPDATE footpath_visualization f SET sidewalk = 'yes' where sidewalk is null and highway in ('footway', 'path', 'cycleway', 'living_street', 'steps', 'pedestrian', 'track');
UPDATE footpath_visualization f SET surface = 'asphalt' where surface IS NULL AND highway IN ('residential','tertiary','secondary','primary','living_street');
UPDATE footpath_visualization f SET surface = NULL where surface not in ('paved','asphalt','concrete','concrete:lanes','paving_stones','cobblestone:flattened','stone',
'sandstone','sett','metal','unhewn_cobblestone','cobblestone','unpaved','compacted','fine_gravel','metal_grid','gravel','pebblestone','rock','wood','ground','dirt','earth','grass','grass_paver','mud','sand');

--calculate score
UPDATE footpath_visualization f SET sidewalk_quality = 
100 * group_index(
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
);

--traffic protection--
--prepara data
DROP TABLE IF EXISTS highway_buffer;
CREATE TABLE highway_buffer as
SELECT ST_BUFFER(w.geom,0.00015) AS geom, lanes, maxspeed_forward
FROM ways w, study_area s 
WHERE highway IN ('living_street','residential','secondary','tertiary','primary')
AND ST_Intersects(w.geom,s.geom);

CREATE INDEX ON highway_buffer USING GIST(geom);

UPDATE footpath_visualization SET maxspeed_forward = NULL WHERE highway IN ('path','track');

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

--calculate score
UPDATE footpath_visualization f SET traffic_protection = 
100 * group_index(
	ARRAY[
		select_weight_walkability_range('lanes',lanes),
		select_weight_walkability_range('maxspeed',maxspeed_forward),
		select_weight_walkability('parking',parking)
	],
	ARRAY[
		select_full_weight_walkability('lanes'),
		select_full_weight_walkability('maxspeed'),
		select_full_weight_walkability('parking')
	]
);

UPDATE footpath_visualization SET traffic_protection = 100
WHERE traffic_protection IS NULL; 

--security--
UPDATE footpath_visualization f SET security = 
(
    select_weight_walkability('lit_classified',lit_classified) 
)
*(100/0.14);
UPDATE footpath_visualization f SET security = 50 WHERE security IS NULL;
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
--Landuse
-- DROP TABLE IF EXISTS buffer_test;
-- CREATE TEMP TABLE buffer_test (id serial, geom geography);
-- INSERT INTO buffer_test
-- SELECT id, st_buffer(geom::geography, 8) AS geom FROM footpath_visualization;

-- DROP TABLE IF EXISTS lu_score;
-- CREATE TABLE lu_score (id serial, score numeric);
-- INSERT INTO lu_score
-- WITH landuses AS (SELECT * FROM landuse_osm lo WHERE landuse = ANY (SELECT sring_condition FROM walkability WHERE attribute = 'land_use')),
-- unique_landuse AS (SELECT DISTINCT b.id, l.landuse AS landuse
-- 	FROM buffer_test b
-- 	LEFT JOIN landuses l ON st_intersects(b.geom::geometry, l.geom)),
-- lu_link AS (SELECT id, count(id) FROM unique_landuse GROUP BY id),
-- max_landuses AS (SELECT max(count) AS max_lu FROM lu_link)
-- SELECT id, ((count::numeric/(SELECT* FROM max_landuses)::NUMERIC)*0.14) AS score FROM lu_link;

-- ALTER TABLE footpath_visualization DROP COLUMN IF EXISTS landuse_score;
-- ALTER TABLE footpath_visualization ADD COLUMN landuse_score NUMERIC;
-- UPDATE footpath_visualization SET landuse_score = score
-- FROM lu_score
-- WHERE lu_score.id = footpath_visualization.id;

UPDATE footpath_visualization f  
SET landuse = 'null'
WHERE landuse IS NULL

UPDATE footpath_visualization f 
SET walking_environment = landuse_score*(100/0.05); 

ALTER TABLE footpath_visualization DROP COLUMN IF EXISTS landuse_score;
-- POIS along the route (issue #986)
-- Pop density (issue #986)
--- Comfort indicators
-- Benches

DROP TABLE IF EXISTS benches;
CREATE TEMP TABLE benches (id serial, total_bench int8);
INSERT INTO benches
WITH buffer AS (
	SELECT id, length_m,  st_buffer(geom::geography, 8) AS geom FROM footpath_visualization),
bench AS (SELECT geom FROM pois WHERE amenity = 'bench')
SELECT b.id, count(bench.geom) AS total_bench
FROM buffer b
LEFT JOIN bench ON st_contains(b.geom::geometry, bench.geom)
GROUP BY b.id;

-- Tag yes or no for function
ALTER TABLE footpath_visualization DROP COLUMN IF EXISTS bench;
ALTER TABLE footpath_visualization ADD COLUMN bench varchar; 
UPDATE footpath_visualization 
SET bench = 'yes' 
FROM benches
WHERE benches.id = footpath_visualization.id AND benches.total_bench >= 1;
UPDATE footpath_visualization 
SET bench = 'no'
FROM benches 
WHERE benches.id = footpath_visualization.id AND benches.total_bench = 0;

-- Slope

UPDATE footpath_visualization 
SET incline_percent = 0 WHERE incline_percent IS NULL;
--SELECT incline_percent, select_weight_walkability_range('slope',incline_percent) FROM footpath_visualization fu ORDER BY incline_percent DESC;

--- Furniture
-- Define general buffer for next point-based measures1
DROP TABLE IF EXISTS buffer_footpaths;
CREATE TABLE buffer_footpaths (id serial, geom geography);

INSERT INTO buffer_footpaths
SELECT id, st_buffer(geom::geography, 8) AS geom FROM footpath_visualization;

DROP TABLE IF EXISTS furniture;
CREATE TEMP TABLE furniture(id serial, total_furniture int8);

INSERT INTO furniture
WITH furniture AS (SELECT geom FROM pois WHERE amenity = 'waste_basket')
SELECT b.id, count(f.geom) AS furniture
FROM buffer_footpaths b
LEFT JOIN furniture f ON st_contains(b.geom::geometry, f.geom)
GROUP BY b.id;

ALTER TABLE footpath_visualization DROP COLUMN IF EXISTS furniture;
ALTER TABLE footpath_visualization ADD COLUMN furniture varchar; 
UPDATE footpath_visualization 
SET furniture = 'yes' 
FROM furniture f
WHERE f.id = footpath_visualization.id AND f.total_furniture >= 1;
UPDATE footpath_visualization 
SET furniture = 'no'
FROM furniture f
WHERE f.id = footpath_visualization.id AND f.total_furniture = 0;

--- Bathrooms
DROP TABLE IF EXISTS toilet;
CREATE TEMP TABLE toilet(id serial, total_toilet int8);

INSERT INTO toilet
WITH toilet AS (SELECT geom FROM pois WHERE amenity = 'toilets')
SELECT b.id, count(t.geom) AS toilet
FROM buffer_footpaths b
LEFT JOIN toilet t ON st_contains(b.geom::geometry, t.geom)
GROUP BY b.id;

ALTER TABLE footpath_visualization DROP COLUMN IF EXISTS toilet;
ALTER TABLE footpath_visualization ADD COLUMN toilet varchar; 
UPDATE footpath_visualization 
SET toilet = 'yes' 
FROM toilet t
WHERE t.id = footpath_visualization.id AND t.total_toilet >= 1;
UPDATE footpath_visualization 
SET toilet = 'no'
FROM toilet t
WHERE t.id = footpath_visualization.id AND t.total_toilet = 0;

--- Drinking fountains
DROP TABLE IF EXISTS drinking;
CREATE TEMP TABLE drinking(id serial, total_drinking int8);

INSERT INTO drinking
WITH drinking AS (SELECT geom FROM pois WHERE amenity = 'drinking_water')
SELECT b.id, count(d.geom) AS total_drinking
FROM buffer_footpaths b
LEFT JOIN drinking d ON st_contains(b.geom::geometry, d.geom)
GROUP BY b.id;

ALTER TABLE footpath_visualization DROP COLUMN IF EXISTS drinking;
ALTER TABLE footpath_visualization ADD COLUMN drinking varchar; 
UPDATE footpath_visualization 
SET drinking = 'yes' 
FROM drinking d
WHERE d.id = footpath_visualization.id AND d.total_drinking >= 1;
UPDATE footpath_visualization 
SET drinking = 'no'
FROM drinking d
WHERE d.id = footpath_visualization.id AND d.total_drinking = 0;

--- Street marking or traffic light
DROP TABLE IF EXISTS marking;
CREATE TEMP TABLE marking(id serial, total_marking int8);

INSERT INTO marking
WITH marking AS (SELECT geom FROM street_crossings WHERE highway = 'crossing' AND crossing = ANY (ARRAY ['marked','traffic_signals']))
SELECT b.id, count(m.geom) AS total_marking
FROM buffer_footpaths b
LEFT JOIN marking m ON st_contains(b.geom::geometry, m.geom)
GROUP BY b.id;

ALTER TABLE footpath_visualization DROP COLUMN IF EXISTS marking;
ALTER TABLE footpath_visualization ADD COLUMN marking varchar; 

UPDATE footpath_visualization 
SET marking = 'yes' 
FROM marking m
WHERE m.id = footpath_visualization.id AND m.total_marking >= 1;
UPDATE footpath_visualization 
SET marking = 'no'
FROM marking m
WHERE m.id = footpath_visualization.id AND m.total_marking = 0;

--- Compile in the footpaths union table 
UPDATE footpath_visualization f SET comfort = 
(
    select_weight_walkability('equipment',bench) +
    select_weight_walkability('toilets',toilet) +
    select_weight_walkability('drinking_fountain',drinking) +
    select_weight_walkability('cross_mark',marking) +
    select_weight_walkability_range('slope', incline_percent)
)
*(100/0.14);

UPDATE footpath_visualization 
SET vegetation = 0 
WHERE vegetation IS NULL; 



ALTER TABLE footpath_visualization DROP COLUMN IF EXISTS bench;
ALTER TABLE footpath_visualization DROP COLUMN IF EXISTS furniture;
ALTER TABLE footpath_visualization DROP COLUMN IF EXISTS toilet;
ALTER TABLE footpath_visualization DROP COLUMN IF EXISTS drinking;
ALTER TABLE footpath_visualization DROP COLUMN IF EXISTS marking;
ALTER TABLE footpath_visualization DROP COLUMN IF EXISTS trees;
ALTER TABLE footpath_visualization DROP COLUMN IF EXISTS green_landuse;


--overall walkability---
UPDATE footpath_visualization f SET walkability = 
(comfort*0.14) + (vegetation*0.28) + (security*0.14) + (traffic_protection*0.14) + (sidewalk_quality*0.29);

