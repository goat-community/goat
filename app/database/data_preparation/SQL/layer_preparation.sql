--THIS FILE NEEDS TO BE EXECUTED TO CREATE ALL NECESSARY TABLES FOR THE STREET LEVEL QUALITY LAYERS

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
		AND w.class_id::text NOT IN (SELECT UNNEST(select_from_variable_container('excluded_class_id_walking'))) 
		AND (w.foot NOT IN (SELECT UNNEST(select_from_variable_container('categories_no_foot'))) 
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
		AND w.class_id::text NOT IN (SELECT UNNEST(select_from_variable_container('excluded_class_id_walking'))) 
		AND (w.foot NOT IN (SELECT UNNEST(select_from_variable_container('categories_no_foot'))) 
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