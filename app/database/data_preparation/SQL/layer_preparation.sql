

--THIS FILE NEEDS TO BE EXECUTED TO CREATE ALL NECESSARY TABLES FOR THE STREET LEVEL QUALITY LAYERS

/*Collect deathends close to buildings*/
DROP TABLE IF EXISTS ways_to_remove;
CREATE TABLE ways_to_remove AS 
SELECT DISTINCT w.id, class_id, w.SOURCE, w.target, 
CASE WHEN death_end = SOURCE THEN SOURCE ELSE target END AS not_death_end_vertex, w.geom
FROM ways w, buildings b
WHERE death_end IS NOT NULL 
AND highway NOT IN ('residential','living_street')
AND ST_DWITHIN(w.geom, b.geom,  3 * meter_degree())
AND w.class_id::text NOT IN (SELECT UNNEST(select_from_variable_container('excluded_class_id_walking'))) 
AND (
	w.foot NOT IN (SELECT UNNEST(select_from_variable_container('categories_no_foot'))) 
	OR w.foot IS NULL 
);

/*Remove deathends shorter then 20 meters*/
ALTER TABLE ways_to_remove ADD PRIMARY KEY(id);
INSERT INTO ways_to_remove
SELECT DISTINCT w.id, w.class_id, w.SOURCE, w.target, 
CASE WHEN w.death_end = w.SOURCE THEN w.SOURCE ELSE w.target END AS not_death_end_vertex, w.geom
FROM (
	SELECT DISTINCT *
	FROM ways 
	WHERE death_end IS NOT NULL 
	AND length_m < 20
	AND highway NOT IN ('residential','living_street')
	AND class_id::text NOT IN (SELECT UNNEST(select_from_variable_container('excluded_class_id_walking'))) 
	AND (
		foot NOT IN (SELECT UNNEST(select_from_variable_container('categories_no_foot'))) 
		OR foot IS NULL 
	)
) w
LEFT JOIN ways_to_remove e
ON w.id = e.id 
WHERE e.id IS NULL; 

/*Remove neighbor edge of deathend if also new deathend*/
INSERT INTO ways_to_remove
SELECT w.id, w.class_id, w.SOURCE, w.target,
CASE WHEN w.death_end = w.SOURCE THEN w.SOURCE ELSE w.target END AS not_death_end_vertex, w.geom
FROM ways_to_remove e, ways_vertices_pgr v, ways w 
WHERE e.not_death_end_vertex = v.id 
AND v.cnt = 2
AND w.highway NOT IN ('residential','living_street')
AND
(
	w.SOURCE = e.not_death_end_vertex 
	OR  
	w.target = e.not_death_end_vertex
)
AND e.id <> w.id
AND w.class_id::text NOT IN (SELECT UNNEST(select_from_variable_container('excluded_class_id_walking'))) 
AND (
	w.foot NOT IN (SELECT UNNEST(select_from_variable_container('categories_no_foot'))) 
	OR w.foot IS NULL 
);

/*TO IMPROVE: Loop through death ends to get new death ends*/

/*Remove linkes that are inside buildings*/
INSERT INTO ways_to_remove (id)
SELECT w.id
FROM (
	SELECT DISTINCT w.id
	FROM ways w, buildings b 
	WHERE ST_Contains(b.geom,w.geom)
) w
LEFT JOIN ways_to_remove e
ON w.id = e.id 
WHERE e.id IS NULL; 

/*Create cleaned ways table and split long links*/
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
LEFT JOIN ways_to_remove e
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
LEFT JOIN ways_to_remove e
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
CREATE TABLE footpath_visualization 
(
	id serial,  
	width float,
	maxspeed integer, 
	incline_percent float, 
	lanes integer,
	noise_day float, 
	noise_night float, 
	lit text,
	lit_classified text, 
	parking text, 
	segregated text, 
	sidewalk TEXT,
	smoothness text, 
	highway text, 
	oneway text, 
	surface text, 
	wheelchair text, 
	wheelchair_classified text, 
	cnt_crossings integer, 
	cnt_accidents integer, 
	cnt_benches integer, 
	cnt_waste_baskets integer,
	cnt_fountains integer, 
	cnt_toilets integer, 
	population text, 
	pois text, 
	landuse text[],
	street_furniture integer,  
	sidewalk_quality integer,
	traffic_protection integer, 
	security integer, 
	vegetation integer, 
	walking_environment integer,
	comfort integer,
	walkability integer, 
	from_offset text,
	geom geometry,
	CONSTRAINT footpath_visualization_pkey PRIMARY KEY(id)
);

INSERT INTO footpath_visualization(geom, sidewalk, width, highway, oneway, maxspeed, incline_percent, 
lanes, lit, lit_classified, parking, segregated, smoothness, surface, wheelchair, wheelchair_classified, from_offset)
SELECT (ST_OffsetCurve(w.geom,  4 * meter_degree(), 'join=round mitre_limit=2.0')) AS geom, w.sidewalk,
CASE WHEN w.sidewalk_left_width IS NOT NULL 
	THEN w.sidewalk_left_width
WHEN w.sidewalk_both_width IS NOT NULL 
	THEN w.sidewalk_both_width
ELSE NULL
END AS width, highway, oneway, maxspeed_forward, incline_percent, lanes, lit, lit_classified, parking, 
segregated, smoothness, surface, wheelchair, wheelchair_classified,
'yes_left' AS from_offset 
FROM ways_cleaned w
WHERE (w.sidewalk = 'both' OR w.sidewalk = 'left' OR (w.sidewalk IS NULL AND highway IN ('secondary','tertiary')))
AND w.class_id::text NOT IN (SELECT UNNEST(select_from_variable_container('excluded_class_id_walking'))) 
AND (
	w.foot NOT IN (SELECT UNNEST(select_from_variable_container('categories_no_foot'))) 
	OR w.foot IS NULL 
);

INSERT INTO footpath_visualization(geom, sidewalk, width, highway, oneway, maxspeed, incline_percent, 
lanes, lit, lit_classified, parking, segregated, smoothness, surface, wheelchair, wheelchair_classified, from_offset)
SELECT (ST_OffsetCurve(w.geom,  -4 * meter_degree(), 'join=round mitre_limit=2.0')) AS geom, w.sidewalk,
CASE WHEN w.sidewalk_right_width IS NOT NULL 
	THEN w.sidewalk_right_width
WHEN w.sidewalk_both_width IS NOT NULL 
	THEN w.sidewalk_both_width
ELSE NULL
END AS width, highway, oneway, maxspeed_forward, incline_percent, lanes, lit, lit_classified, parking, 
segregated, smoothness, surface, wheelchair, wheelchair_classified,
'yes_right' AS from_offset  
FROM ways_cleaned w
WHERE (w.sidewalk = 'both' OR w.sidewalk = 'right' OR (w.sidewalk IS NULL AND highway IN ('secondary','tertiary')))
AND w.class_id::text NOT IN (SELECT UNNEST(select_from_variable_container('excluded_class_id_walking'))) 
AND (w.foot NOT IN (SELECT UNNEST(select_from_variable_container('categories_no_foot'))) 
OR w.foot IS NULL);

INSERT INTO footpath_visualization(geom, sidewalk, width, highway, oneway, maxspeed, incline_percent, 
lanes, lit, lit_classified, parking, segregated, smoothness, surface, wheelchair, wheelchair_classified, from_offset)
SELECT geom, sidewalk, width, highway, oneway, maxspeed_forward, 
incline_percent, lanes, lit, lit_classified, parking, 
segregated, smoothness, surface, wheelchair, wheelchair_classified,
'no' as from_offset 
FROM ways_cleaned
WHERE sidewalk IN ('no','none')
OR highway = 'living_street' 
OR (highway in ('residential','unclassified','service') AND sidewalk IS NULL);

INSERT INTO footpath_visualization(geom, sidewalk, width, highway, oneway, maxspeed, incline_percent, 
lanes, lit, lit_classified, parking, segregated, smoothness, surface, wheelchair, wheelchair_classified, from_offset)
SELECT geom, sidewalk, 
CASE WHEN segregated = 'yes'
	THEN width/2 
ELSE width
END AS width, highway, oneway, maxspeed_forward, incline_percent, lanes, lit, lit_classified, parking,
segregated, smoothness, surface, wheelchair, wheelchair_classified,
'no' AS from_offset
FROM ways_cleaned
WHERE highway ='cycleway' OR (foot = 'designated' AND bicycle = 'designated');

INSERT INTO footpath_visualization(geom, sidewalk, width, highway, oneway, maxspeed, incline_percent, 
lanes, lit, lit_classified, parking, segregated, smoothness, surface, wheelchair, wheelchair_classified, from_offset)
SELECT geom, sidewalk, width, highway, oneway, maxspeed_forward,
incline_percent, lanes, lit, lit_classified, parking, 
segregated, smoothness, surface, wheelchair, wheelchair_classified,
'no' AS from_offset  
FROM ways_cleaned
WHERE sidewalk IS NULL AND highway IN ('path','track','footway','steps','service','pedestrian');

CREATE INDEX ON footpath_visualization USING gist(geom);

/*Overlaps are removed. A logic is implemented that keeps the large geometry when clipped. This can also cause errors.*/
DROP TABLE IF EXISTS splitted_geoms_to_keep;
CREATE TEMP TABLE splitted_geoms_to_keep AS 
SELECT v.id, j.geom
FROM footpath_visualization v 
CROSS JOIN LATERAL 
(
	SELECT (ST_DUMP(ST_SPLIT(v.geom, x.geom))).geom AS geom 
	FROM 
	(
		SELECT ST_UNION(geom) AS geom 
		FROM footpath_visualization fv
		WHERE ST_Intersects(v.geom, fv.geom)
		AND ST_CROSSES(fv.geom, v.geom)
	) x
	WHERE st_geometrytype(ST_Intersection(v.geom,x.geom)) = 'ST_Point' 
	ORDER BY ST_LENGTH((ST_DUMP(ST_SPLIT(v.geom, x.geom))).geom)
	DESC
	LIMIT 1
) j;

CREATE INDEX ON splitted_geoms_to_keep (id);
UPDATE footpath_visualization f
SET geom = g.geom
FROM splitted_geoms_to_keep g
WHERE f.id = g.id;

--Table for visualization of parking
DROP TABLE IF EXISTS parking;
CREATE TABLE parking AS
	SELECT (ST_OffsetCurve(w.geom,  0.00005, 'join=round mitre_limit=2.0')) AS geom, 
		w.parking,
			CASE WHEN w.parking_lane_left IS NOT NULL 
				THEN w.parking_lane_left
			WHEN w.parking_lane_both IS NOT NULL 
				THEN w.parking_lane_both
			ELSE NULL
			END AS parking_lane, 
		highway
	FROM ways_cleaned w
	WHERE (w.parking_lane_left IS NOT NULL OR w.parking_lane_both IS NOT NULL)
UNION
	SELECT (ST_OffsetCurve(w.geom,  -0.00005, 'join=round mitre_limit=2.0')) AS geom, 
		w.parking,
			CASE WHEN w.parking_lane_right IS NOT NULL 
				THEN w.parking_lane_right
			WHEN w.parking_lane_both IS NOT NULL 
				THEN w.parking_lane_both
			ELSE NULL
			END AS parking_lane, 
		highway
	FROM ways_cleaned w
	WHERE (w.parking_lane_right IS NOT NULL OR w.parking_lane_both IS NOT NULL)
UNION
	SELECT (ST_OffsetCurve(w.geom,  0.00005, 'join=round mitre_limit=2.0')), w.parking, 'no' AS parking_lane, w.highway FROM ways_cleaned w
	WHERE w.parking = 'no'
UNION
	SELECT (ST_OffsetCurve(w.geom,  -0.00005, 'join=round mitre_limit=2.0')), w.parking, 'no' AS parking_lane, w.highway FROM ways_cleaned w
	WHERE w.parking = 'no'
UNION
	SELECT geom, parking, NULL AS parking_lane, highway FROM ways_cleaned
	WHERE parking IS NULL AND parking_lane_right IS NULL AND parking_lane_left IS NULL AND parking_lane_both IS NULL
	AND highway IN ('secondary','tertiary','residential','living_street','service','unclassified');
