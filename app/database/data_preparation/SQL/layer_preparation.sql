--THIS FILE NEEDS TO BE EXECUTED TO CREATE ALL NECESSARY TABLES FOR THE STREET LEVEL QUALITY LAYERS
/*Split long ways (length_m >= 200)and remove death_end that are house entrance*/
DROP TABLE IF EXISTS expanded_death_end;
CREATE TABLE expanded_death_end AS 
SELECT DISTINCT w.id, class_id, w.geom
FROM ways w, buildings b
WHERE death_end IS NOT NULL 
AND highway NOT IN ('residential','living_street')
AND ST_DWITHIN(w.geom, b.geom,  3 * meter_degree());

ALTER TABLE expanded_death_end ADD PRIMARY KEY(id);

DROP TABLE IF EXISTS ways_cleaned;
CREATE TABLE ways_cleaned AS 
SELECT w.id AS wid, w.osm_id, w.name, w.class_id, highway, surface, smoothness, maxspeed_forward, maxspeed_backward, bicycle, foot, oneway, crossing,
bicycle_road, cycleway, incline, incline_percent, lit, lit_classified, lanes, parking, parking_lane_both, parking_lane_left,
parking_lane_right, segregated, sidewalk, sidewalk_both_width, sidewalk_left_width, sidewalk_right_width, wheelchair, wheelchair_classified, width,
death_end, split_long_way(w.geom,length_m::numeric,200) AS geom 
FROM (
	SELECT w.* 
	FROM ways w, study_area s 
	WHERE ST_Intersects(w.geom, s.geom)
) w
LEFT JOIN expanded_death_end e
ON w.id = e.id
WHERE e.id IS NULL
AND w.class_id::text NOT IN (SELECT UNNEST(select_from_variable_container('excluded_class_id_walking'))) 
AND (
	w.foot NOT IN (SELECT UNNEST(select_from_variable_container('categories_no_foot'))) 
	OR w.foot IS NULL 
)
AND length_m >= 200;

INSERT INTO ways_cleaned 
SELECT w.id AS wid, w.osm_id, w.name, w.class_id, highway, surface, smoothness, maxspeed_forward, maxspeed_backward, bicycle, foot, oneway, crossing,
bicycle_road, cycleway, incline, incline_percent, lit, lit_classified, lanes, parking, parking_lane_both, parking_lane_left,
parking_lane_right, segregated, sidewalk, sidewalk_both_width, sidewalk_left_width, sidewalk_right_width, wheelchair, wheelchair_classified, width,
death_end, w.geom
FROM (
	SELECT w.* 
	FROM ways w, study_area s 
	WHERE ST_Intersects(w.geom, s.geom)
) w
LEFT JOIN expanded_death_end e
ON w.id = e.id
WHERE e.id IS NULL
AND w.class_id::text NOT IN (SELECT UNNEST(select_from_variable_container('excluded_class_id_walking'))) 
AND (
	w.foot NOT IN (SELECT UNNEST(select_from_variable_container('categories_no_foot'))) 
	OR w.foot IS NULL 
)
AND length_m < 200;

ALTER TABLE ways_cleaned ADD COLUMN id serial; 
CREATE INDEX ON ways_cleaned USING GIST(geom);
ALTER TABLE ways_cleaned ADD PRIMARY KEY(id);

--Table for visualization of the footpath width
DROP TABLE IF EXISTS footpath_visualization;
CREATE TABLE footpath_visualization AS
SELECT (ST_OffsetCurve(w.geom,  4 * meter_degree(), 'join=round mitre_limit=2.0')) AS geom, w.sidewalk,
CASE WHEN w.sidewalk_left_width IS NOT NULL 
	THEN w.sidewalk_left_width
WHEN w.sidewalk_both_width IS NOT NULL 
	THEN w.sidewalk_both_width
ELSE NULL
END AS width, highway, oneway, maxspeed_forward, maxspeed_backward, crossing, incline, 
incline_percent, lanes, lit, lit_classified, parking, parking_lane_both, parking_lane_left, 
parking_lane_right, segregated, smoothness, surface, wheelchair, wheelchair_classified,
'yes_left' AS from_offset 
FROM ways_cleaned w
WHERE (w.sidewalk = 'both' OR w.sidewalk = 'left' OR (w.sidewalk IS NULL AND highway IN ('secondary','tertiary')))
AND w.class_id::text NOT IN (SELECT UNNEST(select_from_variable_container('excluded_class_id_walking'))) 
AND (
	w.foot NOT IN (SELECT UNNEST(select_from_variable_container('categories_no_foot'))) 
	OR w.foot IS NULL 
);

INSERT INTO footpath_visualization
SELECT (ST_OffsetCurve(w.geom,  4 * meter_degree(), 'join=round mitre_limit=2.0')) AS geom, w.sidewalk,
CASE WHEN w.sidewalk_right_width IS NOT NULL 
	THEN w.sidewalk_right_width
WHEN w.sidewalk_both_width IS NOT NULL 
	THEN w.sidewalk_both_width
ELSE NULL
END AS width, highway, oneway, maxspeed_forward, maxspeed_backward, crossing, incline, 
incline_percent, lanes, lit, lit_classified, parking, parking_lane_both, parking_lane_left, 
parking_lane_right, segregated, smoothness, surface, wheelchair, wheelchair_classified,
'yes_right' AS from_offset  
FROM ways_cleaned w
WHERE (w.sidewalk = 'both' OR w.sidewalk = 'right' OR (w.sidewalk IS NULL AND highway IN ('secondary','tertiary')))
AND w.class_id::text NOT IN (SELECT UNNEST(select_from_variable_container('excluded_class_id_walking'))) 
AND (w.foot NOT IN (SELECT UNNEST(select_from_variable_container('categories_no_foot'))) 
OR w.foot IS NULL);

INSERT INTO footpath_visualization
SELECT geom, sidewalk, width, highway, oneway, maxspeed_forward, maxspeed_backward, crossing, incline, 
incline_percent, lanes, lit, lit_classified, parking, parking_lane_both, parking_lane_left, parking_lane_right, 
segregated, smoothness, surface, wheelchair, wheelchair_classified,
'no' as from_offset 
FROM ways_cleaned
WHERE sidewalk IN ('no','none')
OR highway = 'living_street' 
OR (highway in ('residential','unclassified','service') AND sidewalk IS NULL);

INSERT INTO footpath_visualization
SELECT geom, sidewalk, 
CASE WHEN segregated = 'yes'
	THEN width/2 
ELSE width
END AS width, highway, oneway, maxspeed_forward, maxspeed_backward, crossing, incline, 
incline_percent, lanes, lit, lit_classified, parking, parking_lane_both, parking_lane_left, 
parking_lane_right, segregated, smoothness, surface, wheelchair, wheelchair_classified,
'no' AS from_offset
FROM ways_cleaned
WHERE highway ='cycleway' OR (foot = 'designated' AND bicycle = 'designated');

INSERT INTO footpath_visualization
SELECT geom, sidewalk, width, highway, oneway, maxspeed_forward, maxspeed_backward, crossing, incline, 
incline_percent, lanes, lit, lit_classified, parking, parking_lane_both, parking_lane_left, parking_lane_right, 
segregated, smoothness, surface, wheelchair, wheelchair_classified,
'no' AS from_offset  
FROM ways_cleaned
WHERE sidewalk IS NULL AND highway IN ('path','track','footway','steps','service','pedestrian');

CREATE INDEX ON footpath_visualization USING gist(geom);
ALTER TABLE footpath_visualization ADD COLUMN id serial;
ALTER TABLE footpath_visualization ADD PRIMARY KEY(id);
	
--Precalculation of visualized features for illuminance

WITH variables AS 
(
    SELECT select_from_variable_container_o('lit') AS lit
)
UPDATE footpath_visualization f SET lit_classified = x.lit_classified
FROM
    (SELECT f.id,
    CASE WHEN 
        lit IN ('yes','Yes') 
        OR (lit IS NULL AND highway IN (SELECT jsonb_array_elements_text((lit ->> 'highway_yes')::jsonb) FROM variables)
			AND maxspeed_forward<80)
        THEN 'yes' 
    WHEN
        lit IN ('no','No')
        OR (lit IS NULL AND (highway IN (SELECT jsonb_array_elements_text((lit ->> 'highway_no')::jsonb) FROM variables) 
        OR surface IN (SELECT jsonb_array_elements_text((lit ->> 'surface_no')::jsonb) FROM variables)
		OR maxspeed_forward>=80)
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
SELECT (ST_DUMP(ST_UNION(ST_BUFFER(way,15 * meter_degree())))).geom AS geom 
FROM planet_osm_point 
WHERE highway = 'street_lamp';

CREATE INDEX ON buffer_lamps USING gist(geom);

CREATE TEMP TABLE lit_share AS 
SELECT f.id, SUM(ST_LENGTH(ST_Intersection(b.geom, f.geom)))/ST_LENGTH(f.geom) AS share_intersection, f.geom 
FROM buffer_lamps b, footpath_visualization f 
WHERE ST_Intersects(b.geom,f.geom) 
GROUP BY id; 
ALTER TABLE lit_share ADD PRIMARY KEY(id);

UPDATE footpath_visualization f 
SET lit_classified = 'yes'
FROM lit_share l  
WHERE (lit IS NULL OR lit = '') 
AND share_intersection > 0.3
AND f.id = l.id; 

ALTER TABLE footpath_visualization ADD COLUMN IF NOT EXISTS lit_share numeric;

UPDATE footpath_visualization f  
SET lit_share = l.share_intersection
FROM lit_share l 
WHERE f.id = l.id;

DROP TABLE lit_share;
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