--THIS FILE NEEDS TO BE EXECUTED TO CREATE ALL NECESSARY TABLES FOR THE STREET LEVEL QUALITY LAYERS
--Creation of a table that stores all street crossings

ALTER TABLE planet_osm_point 
	ADD COLUMN crossing text, ADD COLUMN traffic_signals text;

UPDATE planet_osm_point p
SET crossing = l.crossing, traffic_signals = l.traffic_signals
FROM (select osm_id, (tags -> 'crossing') AS crossing, 
	(tags -> 'traffic_signals') AS traffic_signals
	from planet_osm_point p) l
WHERE p.osm_id = l.osm_id;

DROP TABLE IF EXISTS crossings;
CREATE TABLE crossings AS
(SELECT osm_id, highway, way, traffic_signals, crossing FROM planet_osm_point WHERE highway = 'crossing' 
	OR (highway = 'traffic_signals' AND traffic_signals = 'pedestrian_crossing'));

ALTER TABLE planet_osm_point 
	ADD COLUMN crossing text, ADD COLUMN traffic_signals text;

UPDATE planet_osm_point p
SET crossing = l.crossing, traffic_signals = l.traffic_signals
FROM (select osm_id, (tags -> 'crossing') AS crossing, 
	(tags -> 'traffic_signals') AS traffic_signals
	from planet_osm_point p) l
WHERE p.osm_id = l.osm_id;

DROP TABLE IF EXISTS crossings;
CREATE TABLE crossings AS
(SELECT osm_id, highway, way, traffic_signals, crossing FROM planet_osm_point WHERE highway = 'crossing' 
	OR (highway = 'traffic_signals' AND traffic_signals = 'pedestrian_crossing'));

ALTER TABLE crossings 
	ADD COLUMN crossing_ref text, 
	ADD COLUMN kerb text, ADD COLUMN segregated text, 
	ADD COLUMN supervised text, ADD COLUMN tactile_paving text,
	ADD COLUMN wheelchair text;
	 
UPDATE crossings 
SET crossing_ref = l.crossing_ref, kerb = l.kerb, segregated = l.segregated, supervised = l.supervised, 
	tactile_paving = l.tactile_paving, wheelchair = l.wheelchair
FROM (select osm_id, (tags -> 'crossing') AS crossing, 
	(tags -> 'crossing_ref') AS crossing_ref, (tags -> 'kerb') AS kerb, 
	(tags -> 'segregated') AS segregated, (tags -> 'supervised') AS supervised, 
	(tags -> 'tactile_paving') AS tactile_paving, (tags -> 'wheelchair') AS wheelchair
	FROM planet_osm_point p) l
WHERE crossings.osm_id = l.osm_id;

--Creation of a table that stores all sidewalk geometries
DROP TABLE IF EXISTS ways_offset_sidewalk;
CREATE TABLE ways_offset_sidewalk AS
SELECT w.id, w.sidewalk,(ST_OffsetCurve(w.geom,  0.00005, 'join=round mitre_limit=2.0')) AS geom_left, 
	(ST_OffsetCurve(w.geom,  -0.00005, 'join=round mitre_limit=2.0')) AS geom_right
FROM ways w
WHERE w.sidewalk = 'both' OR w.sidewalk = 'left' OR w.sidewalk = 'right';

CREATE INDEX ON ways_offset_sidewalk USING btree(id);
CREATE INDEX ON ways_offset_sidewalk USING gist(geom_left);
CREATE INDEX ON ways_offset_sidewalk USING gist(geom_right);

--Table for visualization of the footpath width
DROP TABLE IF EXISTS footpaths_union;
CREATE TABLE footpaths_union AS
	SELECT o.geom_left AS geom, o.sidewalk,
	CASE WHEN w.sidewalk_left_width IS NOT NULL 
		THEN w.sidewalk_left_width
	WHEN w.sidewalk_both_width IS NOT NULL 
		THEN w.sidewalk_both_width
	ELSE NULL
	END AS width, highway
	FROM ways w, ways_offset_sidewalk o
	WHERE w.id=o.id AND (o.sidewalk = 'both' OR o.sidewalk = 'left' OR o.sidewalk IS NULL)
		AND w.class_id::text NOT IN (SELECT unnest(variable_array) from variable_container WHERE identifier = 'excluded_class_id_walking')
		AND (w.foot NOT IN (SELECT UNNEST(variable_array) FROM variable_container WHERE identifier = 'categories_no_foot') 
		OR w.foot IS NULL)
UNION
	SELECT o.geom_right AS geom, o.sidewalk,
	CASE WHEN w.sidewalk_right_width IS NOT NULL 
		THEN w.sidewalk_right_width
	WHEN w.sidewalk_both_width IS NOT NULL 
		THEN w.sidewalk_both_width
	ELSE NULL
	END AS width, highway
	FROM ways w, ways_offset_sidewalk o
	WHERE w.id=o.id AND (o.sidewalk = 'both' OR o.sidewalk = 'right' OR o.sidewalk IS NULL)
		AND w.class_id::text NOT IN (SELECT unnest(variable_array) from variable_container WHERE identifier = 'excluded_class_id_walking')
		AND (w.foot NOT IN (SELECT UNNEST(variable_array) FROM variable_container WHERE identifier = 'categories_no_foot') 
		OR w.foot IS NULL)
UNION
	SELECT geom, sidewalk, width, highway FROM ways
	WHERE sidewalk = 'no'
UNION
	SELECT geom, sidewalk, width, highway FROM ways
	WHERE highway = 'living_street'
UNION
	SELECT geom, sidewalk, 
	CASE WHEN segregated = 'yes'
		THEN width/2 
	ELSE width
	END AS width, highway 
	FROM ways
	WHERE highway ='cycleway' OR (foot = 'designated' AND bicycle = 'designated')
UNION
	SELECT geom, sidewalk, width, highway FROM ways
	WHERE sidewalk IS NULL AND highway IN ('path','track','footway','steps','service','pedestrian');

CREATE INDEX ON footpaths_union USING gist(geom);
ALTER TABLE footpaths_union ADD COLUMN id serial;
ALTER TABLE footpaths_union ADD PRIMARY KEY(id);

--Creation of a table that stores all parking geometries
DROP TABLE IF EXISTS ways_offset_parking;
CREATE TABLE ways_offset_parking AS
SELECT w.id, w.parking,(ST_OffsetCurve(w.geom,  0.00005, 'join=round mitre_limit=2.0')) AS geom_left, 
	(ST_OffsetCurve(w.geom,  -0.00005, 'join=round mitre_limit=2.0')) AS geom_right
FROM ways w
WHERE w.parking IS NOT NULL OR w.parking_lane_both IS NOT NULL OR w.parking_lane_left IS NOT NULL OR w.parking_lane_right IS NOT NULL;

CREATE INDEX ON ways_offset_parking USING btree(id);
CREATE INDEX ON ways_offset_parking USING gist(geom_left);
CREATE INDEX ON ways_offset_parking USING gist(geom_right);

--Table for visualization of parking
DROP TABLE IF EXISTS parking;
CREATE TABLE parking AS
	SELECT o.geom_left AS geom, 
		w.parking,
			CASE WHEN w.parking_lane_left IS NOT NULL 
				THEN w.parking_lane_left
			WHEN w.parking_lane_both IS NOT NULL 
				THEN w.parking_lane_both
			ELSE NULL
			END AS parking_lane, 
		highway
	FROM ways w, ways_offset_parking o
	WHERE w.id=o.id AND (w.parking_lane_left IS NOT NULL OR w.parking_lane_both IS NOT NULL)
UNION
	SELECT o.geom_right AS geom, 
		w.parking,
			CASE WHEN w.parking_lane_right IS NOT NULL 
				THEN w.parking_lane_right
			WHEN w.parking_lane_both IS NOT NULL 
				THEN w.parking_lane_both
			ELSE NULL
			END AS parking_lane, 
		highway
	FROM ways w, ways_offset_parking o
	WHERE w.id=o.id AND (w.parking_lane_right IS NOT NULL OR w.parking_lane_both IS NOT NULL)
UNION
	SELECT o.geom_left, w.parking, 'no' AS parking_lane, w.highway FROM ways w, ways_offset_parking o
	WHERE w.id=o.id AND w.parking = 'no'
UNION
	SELECT o.geom_right, w.parking, 'no' AS parking_lane, w.highway FROM ways w, ways_offset_parking o
	WHERE w.id=o.id AND w.parking = 'no'
UNION
	SELECT geom, parking, NULL AS parking_lane, highway FROM ways
	WHERE parking IS NULL AND parking_lane_right IS NULL AND parking_lane_left IS NULL AND parking_lane_both IS NULL
	AND highway IN ('secondary','tertiary','residential','living_street','service','unclassified');

--Drop tables that are no further needed
DROP TABLE ways_offset_parking;
DROP TABLE ways_offset_sidewalk;