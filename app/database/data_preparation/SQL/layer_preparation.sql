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

-- TODO: kleine Wege die Dead-ends & highway IN (service, footpath) oder NULL sind rausfiltern -> function "extendline" (IN DREGREE)-> verschneiden mit gebäuden 
-- TODO: Split WAYS 



--Table for visualization of the footpath width
DROP TABLE IF EXISTS footpath_visualization;
CREATE TABLE footpath_visualization AS
SELECT x.* 
FROM 
(
	SELECT o.geom_left AS geom, o.sidewalk,
	CASE WHEN w.sidewalk_left_width IS NOT NULL 
		THEN w.sidewalk_left_width
	WHEN w.sidewalk_both_width IS NOT NULL 
		THEN w.sidewalk_both_width
	ELSE NULL
	END AS width, highway, length_m, oneway, maxspeed_forward, maxspeed_backward, crossing, incline, 
	incline_percent, lanes, lit, lit_classified, parking, parking_lane_both, parking_lane_left, 
	parking_lane_right, segregated, smoothness, surface, wheelchair, wheelchair_classified,
	'yes_left' as offset 
	FROM ways w, ways_offset_sidewalk o
	WHERE w.id=o.id 
	AND (o.sidewalk = 'both' OR o.sidewalk = 'left' OR o.sidewalk IS NULL)
	AND w.class_id::text NOT IN (SELECT UNNEST(select_from_variable_container('excluded_class_id_walking'))) 
	AND (
		w.foot NOT IN (SELECT UNNEST(select_from_variable_container('categories_no_foot'))) 
		OR w.foot IS NULL 
	)
UNION
	SELECT o.geom_right AS geom, o.sidewalk,
	CASE WHEN w.sidewalk_right_width IS NOT NULL 
		THEN w.sidewalk_right_width
	WHEN w.sidewalk_both_width IS NOT NULL 
		THEN w.sidewalk_both_width
	ELSE NULL
	END AS width, highway, length_m, oneway, maxspeed_forward, maxspeed_backward, crossing, incline, 
	incline_percent, lanes, lit, lit_classified, parking, parking_lane_both, parking_lane_left, 
	parking_lane_right, segregated, smoothness, surface, wheelchair, wheelchair_classified,
	'yes_right' as offset  
	FROM ways w, ways_offset_sidewalk o
	WHERE w.id=o.id AND (o.sidewalk = 'both' OR o.sidewalk = 'right' OR o.sidewalk IS NULL)
	AND w.class_id::text NOT IN (SELECT UNNEST(select_from_variable_container('excluded_class_id_walking'))) 
	AND (w.foot NOT IN (SELECT UNNEST(select_from_variable_container('categories_no_foot'))) 
	OR w.foot IS NULL)
UNION
	SELECT geom, sidewalk, width, highway, length_m, oneway, maxspeed_forward, maxspeed_backward, crossing, incline, 
	incline_percent, lanes, lit, lit_classified, parking, parking_lane_both, parking_lane_left, parking_lane_right, 
	segregated, smoothness, surface, wheelchair, wheelchair_classified,
	'no' as offset 
	FROM ways
	WHERE sidewalk = 'no' -- mit nächstem zusammenfassen
UNION
	SELECT geom, sidewalk, width, highway, length_m, oneway, maxspeed_forward, maxspeed_backward, crossing, incline, 
	incline_percent, lanes, lit, lit_classified, parking, parking_lane_both, parking_lane_left, parking_lane_right, 
	segregated, smoothness, surface, wheelchair, wheelchair_classified,
	'no' as offset   
	FROM ways
	WHERE highway = 'living_street' OR (highway in ('residential','unclassified') AND sidewalk IS NULL)
UNION
	SELECT geom, sidewalk, 
	CASE WHEN segregated = 'yes'
		THEN width/2 
	ELSE width
	END AS width, highway, length_m, oneway, maxspeed_forward, maxspeed_backward, crossing, incline, 
	incline_percent, lanes, lit, lit_classified, parking, parking_lane_both, parking_lane_left, 
	parking_lane_right, segregated, smoothness, surface, wheelchair, wheelchair_classified,
	'no' as offset  
	FROM ways
	WHERE highway ='cycleway' OR (foot = 'designated' AND bicycle = 'designated')
UNION
	SELECT geom, sidewalk, width, highway, length_m, oneway, maxspeed_forward, maxspeed_backward, crossing, incline, 
	incline_percent, lanes, lit, lit_classified, parking, parking_lane_both, parking_lane_left, parking_lane_right, 
	segregated, smoothness, surface, wheelchair, wheelchair_classified,
	'no' as offset    
	FROM ways
	WHERE sidewalk IS NULL AND highway IN ('path','track','footway','steps','service','pedestrian')
) x, study_area s 
WHERE ST_intersects(x.geom,s.geom);


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
CREATE TEMP TABLE buffer_lamps as
SELECT ST_BUFFER(way,0.00015,'quad_segs=8') AS geom 
FROM planet_osm_point 
WHERE highway = 'street_lamp';

CREATE INDEX ON buffer_lamps USING gist(geom);

/*
WITH union_b AS 
(
	SELECT ST_UNION(bl.geom) 
	FROM buffer_lamps bl
)
UPDATE ways w SET lit_classified = 'yes'
FROM buffer_lamps b, union_b ub
WHERE (lit IS NULL OR lit = '')
AND ST_Intersects(b.geom,w.geom)
AND ST_Length(ST_Intersection(ub.st_union, w.geom))/ST_Length(w.geom) > 0.3;
*/

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