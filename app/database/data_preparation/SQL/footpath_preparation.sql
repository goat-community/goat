/*Defines maxspeed based on neighboring links and assumption per highway category.*/
DROP TABLE IF EXISTS ways_maxspeed; 
CREATE TEMP TABLE ways_maxspeed AS 
SELECT w.id, w.highway, w.SOURCE, w.target, w.maxspeed_forward, 
CASE WHEN (p.tags -> 'maxspeed')~E'^\\d+$' THEN (p.tags -> 'maxspeed')::integer ELSE NULL END AS maxspeed, w.geom   
FROM ways w, planet_osm_line p 
WHERE maxspeed_forward IS NOT NULL
AND w.osm_id = p.osm_id; 

ALTER TABLE ways_maxspeed ADD PRIMARY KEY(id);
CREATE INDEX ON ways_maxspeed (SOURCE); 
CREATE INDEX ON ways_maxspeed (target); 


DROP TABLE IF EXISTS maxspeed_not_defined;
CREATE TEMP TABLE maxspeed_not_defined AS 
SELECT DISTINCT w2.id, w2.highway, w2.SOURCE, w2.target, w2.maxspeed, w2.geom
FROM ways_maxspeed w2 
WHERE w2.maxspeed IS NULL 
AND w2.highway IN ('motorway','motorway_link','primary','primary_link','secondary','secondary_link','trunk','trunk_link','tertiary','tertiary_link','residential','service','unclassified');

ALTER TABLE maxspeed_not_defined ADD PRIMARY KEY(id);
CREATE INDEX ON maxspeed_not_defined (SOURCE); 
CREATE INDEX ON maxspeed_not_defined (target); 

DROP TABLE IF EXISTS maxspeed_complemented;
CREATE TEMP TABLE maxspeed_complemented
(
	id integer,
	highway TEXT,
	SOURCE integer,
	target integer, 
	maxspeed integer,
	geom geometry
);

DO $$
	DECLARE 
		way_id integer;
		cnt integer := 0;
	BEGIN 
		
		DROP TABLE IF EXISTS result_recursive;
		CREATE TABLE result_recursive
		(
			id integer,
			highway TEXT,
			SOURCE integer,
			target integer, 
			maxspeed integer,
			geom geometry
		);

		FOR way_id IN 
		SELECT DISTINCT w1.id
		FROM ways_maxspeed w1, ways_maxspeed w2 
		WHERE w1.maxspeed IS NOT NULL 
		AND w2.maxspeed IS NULL 
		AND w1.highway IN ('motorway','motorway_link','primary','primary_link','secondary','secondary_link','trunk','trunk_link','tertiary','tertiary_link','residential','service','unclassified')
		AND w2.highway IN ('motorway','motorway_link','primary','primary_link','secondary','secondary_link','trunk','trunk_link','tertiary','tertiary_link','residential','service','unclassified')
		AND (
			(w1.SOURCE = w2.SOURCE OR w1.target = w2.target)
			OR 
			(w1.SOURCE = w2.target OR w1.target = w2.source)
		)		
		LOOP 
		
			cnt = cnt + 1;
			IF (SELECT count(*) FROM (SELECT * FROM maxspeed_not_defined LIMIT 1) x) = 0 THEN
				EXIT;
			END IF; 
	
			TRUNCATE result_recursive; 
			INSERT INTO result_recursive
			WITH RECURSIVE subordinates AS (
				SELECT id, highway, SOURCE, target, maxspeed, geom
				FROM ways_maxspeed 
				WHERE id = way_id
				UNION
				SELECT w.id, w.highway, w.SOURCE, w.target, s.maxspeed, w.geom
				FROM maxspeed_not_defined w, subordinates s
				WHERE s.highway = w.highway
				AND 
				(
					(s.SOURCE = w.SOURCE OR s.target = w.target)
					OR 
					(s.SOURCE = w.target OR s.target = w.source)
				)
			) 
			SELECT *
			FROM subordinates;
				
			DELETE FROM maxspeed_not_defined n
			USING result_recursive r
			WHERE n.id = r.id; 
		
			INSERT INTO maxspeed_complemented 
			SELECT * 
			FROM result_recursive; 
		END LOOP; 
		DROP TABLE result_recursive;
	END; 
$$;

ALTER TABLE maxspeed_complemented ADD PRIMARY KEY(id);

DO $$
	DECLARE 
		backup_speed_classification jsonb := '{
			"path": 5,
			"track": 10,
			"steps": 0,
			"residential": 30,
			"motorway": 130,
			"motorway_link": 80,
			"trunk": 100,
			"trunk_link": 80,
			"footway": 5,
		    "pedestrian": 5,
			"living_street": 7
		}'::jsonb; 
	BEGIN 
		DROP TABLE IF EXISTS classified_maxspeed;
		CREATE TEMP TABLE classified_maxspeed AS 
		SELECT w.id, w.highway, 
		CASE WHEN c.maxspeed IS NOT NULL THEN c.maxspeed 
		WHEN w.maxspeed IS NULL THEN (backup_speed_classification ->> w.highway)::integer
		ELSE w.maxspeed END AS maxspeed, w.geom  
		FROM ways_maxspeed w
		LEFT JOIN maxspeed_complemented c  
		ON w.id = c.id; 
		ALTER TABLE classified_maxspeed ADD PRIMARY KEY(id);
		
		UPDATE ways w
		SET maxspeed_forward = c.maxspeed
		FROM classified_maxspeed c
		WHERE c.id = w.id; 
	END; 
$$;

/*Collect deathends close to buildings*/
DO $$
	DECLARE 
    	buffer float := meter_degree() * 3;
    BEGIN 
		DROP TABLE IF EXISTS ways_to_remove;
		CREATE TABLE ways_to_remove AS
		SELECT DISTINCT w.id, class_id, w.SOURCE, w.target, 
		CASE WHEN death_end = SOURCE THEN SOURCE ELSE target END AS not_death_end_vertex, w.geom
		FROM ways w, buildings b
		WHERE death_end IS NOT NULL 
		AND highway NOT IN ('residential','living_street')
		AND ST_DWITHIN(w.geom, b.geom, buffer)
		AND w.class_id::text NOT IN (SELECT UNNEST(select_from_variable_container('excluded_class_id_walking'))) 
		AND (
			w.foot NOT IN (SELECT UNNEST(select_from_variable_container('categories_no_foot'))) 
			OR w.foot IS NULL 
		);
	END; 
$$;

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

WITH do_not_remove AS 
(
	SELECT w.id 
	FROM planet_osm_line p, ways w 
	WHERE p.highway IS NOT NULL 
	AND 
	(
		covered <> 'no' 
		OR tunnel IN ('yes','covered','building_passage')
		OR bridge IS NOT NULL 
	) 
	AND w.osm_id = p.osm_id 
)
DELETE 
FROM ways_to_remove w 
USING do_not_remove d 
WHERE w.id = d.id; 

/*Create cleaned ways table and split long links*/
DROP TABLE IF EXISTS ways_cleaned;
CREATE TABLE ways_cleaned AS 
SELECT w.id AS wid, w.osm_id, w.name, w.class_id, highway, surface, smoothness, maxspeed_forward, maxspeed_backward, bicycle, foot, oneway, crossing,
bicycle_road, cycleway, incline, incline_percent, lit, lit_classified, lanes, parking, parking_lane_both, parking_lane_left,
parking_lane_right, segregated, sidewalk, sidewalk_both_width, sidewalk_left_width, sidewalk_right_width, wheelchair, wheelchair_classified, width,
death_end, split_long_way(w.geom,length_m::numeric,200) AS geom 
FROM (
	SELECT w.* 
	FROM ways w, study_area_union s 
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
	FROM ways w, study_area_union s 
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
	ways_id bigint,
	osm_id bigint,
	length_m float,
	width jsonb,
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
	surface text, 
	covered text,
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
	vegetation integer, 
	water integer,
	street_furniture integer,  
	sidewalk_quality integer,
	traffic_protection integer, 
	security integer, 
	green_blue_index integer,
	liveliness integer,
	comfort integer,
	walkability integer, 
	data_quality float,
	geom geometry,
	CONSTRAINT footpath_visualization_pkey PRIMARY KEY(id)
);

INSERT INTO footpath_visualization(ways_id, osm_id, length_m, geom, sidewalk, width, highway, maxspeed, incline_percent, 
lanes, lit, lit_classified, parking, segregated, smoothness, surface, wheelchair, wheelchair_classified)
SELECT id, osm_id, ST_LENGTH(geom::geography), geom, w.sidewalk,
CASE WHEN w.sidewalk_left_width IS NOT NULL OR w.sidewalk_right_width IS NOT NULL OR w.sidewalk_both_width IS NOT NULL 
THEN jsonb_build_object('sidewalk_left_width',sidewalk_left_width, 'sidewalk_right_width', sidewalk_right_width, 'sidewalk_both_width', sidewalk_both_width) 
WHEN w.width IS NOT NULL THEN jsonb_build_object('width', width) 
ELSE NULL
END AS width, highway, maxspeed_forward, incline_percent, lanes, lit, lit_classified, parking, 
segregated, smoothness, surface, wheelchair, wheelchair_classified
FROM ways_cleaned w
WHERE w.class_id::text NOT IN (SELECT UNNEST(select_from_variable_container('excluded_class_id_walking'))) 
AND (
	w.foot NOT IN (SELECT UNNEST(select_from_variable_container('categories_no_foot'))) 
	OR w.foot IS NULL 
)
AND highway IS NOT NULL;

CREATE INDEX ON footpath_visualization USING gist(geom);

WITH clipped_foothpaths AS 
(
	SELECT f.id, ST_Intersection(f.geom, s.geom) AS geom 
	FROM footpath_visualization f, study_area_union s 
	WHERE ST_Intersects(f.geom, st_boundary(s.geom)) 
)
UPDATE footpath_visualization f
SET geom = c.geom 
FROM clipped_foothpaths c 
WHERE f.id = c.id; 

WITH to_delete AS 
(
	SELECT id
	FROM footpath_visualization f
	LEFT JOIN study_area s 
	ON ST_Intersects(f.geom, s.geom)
	WHERE s.name IS NULL 
)
DELETE FROM footpath_visualization f 
USING to_delete d
WHERE f.id = d.id;

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
