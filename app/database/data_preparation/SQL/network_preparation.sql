ALTER TABLE ways
DROP COLUMN RULE,DROP COLUMN x1,DROP COLUMN x2,DROP COLUMN y1,DROP COLUMN y2, DROP COLUMN priority,
DROP COLUMN length,DROP COLUMN cost,DROP COLUMN reverse_cost, DROP COLUMN cost_s, DROP COLUMN reverse_cost_s, 
DROP COLUMN source_osm, DROP COLUMN target_osm;

ALTER TABLE ways_vertices_pgr DROP COLUMN chk, DROP COLUMN ein, DROP COLUMN eout, DROP COLUMN lon, DROP COLUMN lat;

ALTER TABLE ways rename column gid to id;
ALTER TABLE ways rename column the_geom to geom;
ALTER TABLE ways_vertices_pgr rename column the_geom to geom;
ALTER TABLE ways alter column target type int4;
ALTER TABLE ways alter column source type int4;

ALTER TABLE ways 
ADD COLUMN bicycle text, ADD COLUMN foot TEXT; 

UPDATE ways 
SET foot = p.foot
FROM planet_osm_line p
WHERE ways.osm_id = p.osm_id
AND p.highway NOT IN('bridleway','cycleway','footway');

UPDATE ways 
SET bicycle = p.bicycle
FROM planet_osm_line p
WHERE ways.osm_id = p.osm_id;

--	ADD COLUMN crossing TEXT, ADD COLUMN one_link_crossing boolean;

--Create table that stores all street crossings

DROP TABLE IF EXISTS street_crossings;
CREATE TABLE street_crossings AS 
SELECT osm_id, highway,(tags -> 'crossing') AS crossing, 
(tags -> 'traffic_signals') AS traffic_signals,(tags -> 'crossing_ref') AS crossing_ref, (tags -> 'kerb') AS kerb, 
(tags -> 'segregated') AS segregated, (tags -> 'supervised') AS supervised, 
(tags -> 'tactile_paving') AS tactile_paving, (tags -> 'wheelchair') AS wheelchair, way AS geom
FROM planet_osm_point p
WHERE (tags -> 'crossing') IS NOT NULL 
OR highway IN('crossing','traffic_signals')
OR (tags -> 'traffic_signals') = 'pedestrian_crossing';

UPDATE street_crossings 
SET crossing = crossing_ref 
WHERE crossing_ref IS NOT NULL;

UPDATE street_crossings 
SET crossing = 'traffic_signals'
WHERE traffic_signals = 'crossing' 
OR traffic_signals = 'pedestrian_crossing';

UPDATE street_crossings 
SET crossing = highway 
WHERE crossing IS NULL AND highway IS NOT NULL; 

ALTER TABLE street_crossings ADD COLUMN gid serial;
ALTER TABLE street_crossings ADD PRIMARY key(gid);
CREATE INDEX ON street_crossings USING GIST(geom);

--Identify ways that intersect with street crossings
DROP TABLE IF EXISTS ways_crossed;
CREATE TABLE ways_crossed AS 
SELECT w.*, c.gid AS crossing_gid, c.crossing
FROM street_crossings c, ways w 
WHERE ST_Intersects(c.geom,w.geom)
AND w.class_id::text NOT IN (SELECT UNNEST(select_from_variable_container('excluded_class_id_walking')))
AND w.class_id::text NOT IN (SELECT UNNEST(select_from_variable_container('excluded_class_id_cycling')))
AND (
(w.foot NOT IN (SELECT UNNEST(select_from_variable_container('categories_no_foot'))) OR foot IS NULL)
OR
(w.bicycle NOT IN (SELECT UNNEST(select_from_variable_container('bicycle'))) OR bicycle IS NULL))
AND c.crossing = 'traffic_signals';

--Check if crossing intersects on or more ways
ALTER TABLE ways_crossed ADD COLUMN one_link_crossing boolean; 

UPDATE ways_crossed w
SET one_link_crossing = x.one_link_crossing
FROM
(
	SELECT CASE WHEN count(*) = 1 THEN TRUE ELSE FALSE END AS one_link_crossing, crossing_gid
	FROM ways_crossed
	GROUP BY crossing_gid
) x 
WHERE w.crossing_gid = x.crossing_gid;

--Create a temporary composite type
DROP TYPE temp_composite CASCADE;
CREATE TYPE temp_composite 
AS (
	new_geom1 geometry,
	source1 integer,
	target1 integer, 
	new_geom2 geometry,
	source2 integer,
	target2 integer, 
	new_vgeom geometry
);

--Split ways where length_m > 20m at intersection and derive new geometries 
DROP TABLE IF EXISTS w_split;
CREATE TEMP TABLE w_split AS  
SELECT w.id, 
CASE WHEN ST_Intersects(st_startpoint(w.geom),c.geom)
THEN ROW(ST_LINESUBSTRING(w.geom,0,(1/length_m)),w.SOURCE,NULL,ST_LINESUBSTRING(w.geom,(1/w.length_m),1),NULL,w.target,ST_endpoint(ST_LINESUBSTRING(w.geom,0,(1/w.length_m))))::temp_composite  
WHEN ST_Intersects(st_endpoint(w.geom),c.geom) 
THEN ROW(ST_LINESUBSTRING(w.geom,1-(1/length_m),1),NULL,w.target,ST_LINESUBSTRING(w.geom,0,1-(1/length_m)),w.SOURCE,NULL,ST_startpoint(ST_LINESUBSTRING(w.geom,1-(1/length_m),1)))::temp_composite 
ELSE NULL END AS features,1 AS length1, (length_m - 1) AS length2 
FROM ways_crossed w, street_crossings c
WHERE one_link_crossing = FALSE 
AND length_m > 20
AND ST_INTERSECTS(w.geom,c.geom);

ALTER TABLE ways ADD COLUMN crossing text; 
ALTER TABLE ways ADD COLUMN one_link_crossing boolean; 

--Insert new vertices into table
INSERT INTO ways_vertices_pgr(geom) 
SELECT (features).new_vgeom
FROM w_split;

--Insert routing network into ways table 
INSERT INTO ways(class_id,length_m,name,SOURCE,target,one_way,maxspeed_forward,maxspeed_backward,osm_id,geom,bicycle,foot,crossing,one_link_crossing)
WITH new_ways AS (
	SELECT id,(features).new_geom1 AS geom,(features).source1 AS SOURCE,(features).target1 AS target, length1 AS length_m, (features).new_vgeom AS v_geom
	FROM w_split s
	UNION ALL 
	SELECT id,(features).new_geom2 AS geom, (features).source2 AS SOURCE,(features).target2 AS target, length2 AS length_m, (features).new_vgeom AS v_geom
	FROM w_split s
)
SELECT w.class_id, n.length_m, w.name, 
CASE WHEN n.SOURCE IS NULL THEN v.id ELSE n.SOURCE END AS SOURCE, 
CASE WHEN n.target IS NULL THEN v.id ELSE n.target END AS target, 
w.one_way, w.maxspeed_forward, w.maxspeed_backward, w.osm_id, n.geom, w.bicycle, w.foot, 'traffic_signals',FALSE
FROM new_ways n, ways w, ways_vertices_pgr v
WHERE n.id = w.id
AND n.geom IS NOT NULL
AND n.v_geom = v.geom;

--Delete original ways that were split
DELETE FROM ways w 
USING w_split s 
WHERE w.id = s.id;

--Assign crossing mode of link
UPDATE ways w SET crossing = c.crossing, one_link_crossing = c.one_link_crossing
FROM ways_crossed c
WHERE w.id = c.id;

ALTER TABLE ways ADD COLUMN crossing_delay_category SMALLINT; 
UPDATE ways 
SET crossing_delay_category = 1
WHERE crossing = 'traffic_signals' 
AND one_link_crossing IS FALSE;

UPDATE ways 
SET crossing_delay_category = 2
WHERE crossing = 'traffic_signals' 
AND one_link_crossing IS TRUE;

DROP TYPE IF EXISTS temp_composite CASCADE;
DROP TABLE IF EXISTS ways_crossed;
--Create columns for further way attributes
ALTER TABLE ways 
ADD COLUMN bicycle_road text, ADD COLUMN cycleway text, 
ADD COLUMN highway text, ADD COLUMN incline text, ADD COLUMN incline_percent integer,
ADD COLUMN lanes NUMERIC, ADD COLUMN lit text, ADD COLUMN lit_classified text, ADD COLUMN parking text, 
ADD COLUMN parking_lane_both text, ADD COLUMN parking_lane_right text, ADD COLUMN parking_lane_left text, 
ADD COLUMN segregated text, ADD COLUMN sidewalk text, ADD COLUMN sidewalk_both_width NUMERIC, 
ADD COLUMN sidewalk_left_width NUMERIC, ADD COLUMN sidewalk_right_width NUMERIC, ADD COLUMN smoothness text, 
ADD COLUMN surface text, ADD COLUMN wheelchair text, ADD COLUMN wheelchair_classified text, ADD COLUMN width NUMERIC;

UPDATE ways_vertices_pgr v SET cnt = y.cnt
FROM (
	SELECT SOURCE, count(source) cnt 
	FROM 
	(
		SELECT SOURCE FROM ways 
		UNION ALL
		SELECT target FROM ways 
	) x 
	GROUP BY SOURCE 
) y
WHERE v.id = y.SOURCE;

UPDATE ways 
SET highway = p.highway, surface = p.surface, width = (CASE WHEN p.width ~ '^[0-9.]*$' THEN p.width::numeric ELSE NULL END),
	bicycle_road = (tags -> 'bicycle_road'), cycleway = (tags -> 'cycleway'), incline = (tags -> 'incline'), lit = (tags -> 'lit'), parking = (tags -> 'parking'), 
	parking_lane_both = (tags -> 'parking:lane:both') , parking_lane_right = (tags -> 'parking:lane:right'), 
	parking_lane_left = (tags -> 'parking:lane:left'), segregated = (tags -> 'segregated'),
	sidewalk = (tags -> 'sidewalk'), smoothness = (tags -> 'smoothness'), wheelchair = (tags -> 'wheelchair'),
	lanes = (tags -> 'lanes')::numeric, sidewalk_both_width = (tags -> 'sidewalk:both:width')::numeric, sidewalk_left_width = (tags -> 'sidewalk:left:width')::numeric,
	sidewalk_right_width = (tags -> 'sidewalk:right:width')::numeric
FROM planet_osm_line p
WHERE ways.osm_id = p.osm_id;

UPDATE ways
SET incline_percent=xx.incline_percent::integer 
FROM (
	SELECT id, regexp_REPLACE(incline,'[^0-9]+','','g') AS incline_percent
	FROM ways
) xx 
WHERE xx.incline_percent IS NOT NULL AND xx.incline_percent <> '' 
AND ways.id = xx.id;

--Updating default speed limits for living_streets
UPDATE ways
SET maxspeed_forward = 7, maxspeed_backward = 7
WHERE highway = 'living_street' AND maxspeed_forward = 50;

--Precalculation of visualized features for wheelchair
WITH variables AS 
(
    SELECT select_from_variable_container_o('wheelchair')  AS wheelchair,
    select_from_variable_container('excluded_class_id_walking') AS excluded_class_id_walking,
    select_from_variable_container('categories_no_foot') AS categories_no_foot,
    select_from_variable_container('categories_sidewalk_no_foot') AS categories_sidewalk_no_foot
) 
UPDATE ways w SET wheelchair_classified = x.wheelchair_classified
FROM
    (SELECT w.id,
    CASE WHEN 
        wheelchair IN ('yes','Yes') 
        OR (wheelchair IS NULL 
			AND sidewalk IN ('both','left','right')
            AND (sidewalk_both_width >= 1.80 OR sidewalk_left_width >= 1.80 OR sidewalk_right_width >= 1.80)
			AND (incline_percent IS NULL OR incline_percent < 6) 
			)
        OR (wheelchair IS NULL AND width >= 1.80 AND highway <> 'steps' 
            AND (smoothness IS NULL 
				OR (smoothness NOT IN (SELECT jsonb_array_elements_text((wheelchair ->> 'smoothness_no')::jsonb) FROM variables)
            		AND smoothness NOT IN (SELECT jsonb_array_elements_text((wheelchair ->> 'smoothness_limited')::jsonb) FROM variables)
           			)
				)
            AND (surface IS NULL 
				OR (surface NOT IN (SELECT jsonb_array_elements_text((wheelchair ->> 'surface_no')::jsonb) FROM variables)
					AND surface NOT IN (SELECT jsonb_array_elements_text((wheelchair ->> 'surface_limited')::jsonb) FROM variables)
					)
				)
            AND (incline_percent IS NULL OR incline_percent < 6)
            )
        OR (wheelchair IS NULL AND highway IN (SELECT jsonb_array_elements_text((wheelchair ->> 'highway_onstreet_yes')::jsonb) FROM variables))
        THEN 'yes'
    WHEN
        wheelchair IN ('limited','Limited')
        OR ( sidewalk IN ('both','left','right')
            AND (
                (sidewalk_both_width < 1.80 OR sidewalk_left_width < 1.80 OR sidewalk_right_width < 1.80 OR 
                (sidewalk_both_width IS NULL AND sidewalk_left_width IS NULL AND sidewalk_right_width IS NULL)
                )
            ) 
            OR (wheelchair IS NULL AND width >= 0.90 AND highway <> 'steps' 
            AND (smoothness IS NULL OR smoothness NOT IN (SELECT jsonb_array_elements_text((wheelchair ->> 'smoothness_no')::jsonb) FROM variables)) 
            AND (surface IS NULL OR surface NOT IN (SELECT jsonb_array_elements_text((wheelchair ->> 'surface_no')::jsonb) FROM variables))
            AND (incline_percent IS NULL OR incline_percent < 6)
            ))
        OR (wheelchair IS NULL AND highway IN (SELECT jsonb_array_elements_text((wheelchair ->> 'highway_onstreet_limited')::jsonb) FROM variables))
        THEN 'limited'
    WHEN
        wheelchair IN ('no','No')
            OR (wheelchair IS NULL AND (width < 0.90 OR highway = 'steps' 
                OR smoothness IN (SELECT jsonb_array_elements_text((wheelchair ->> 'smoothness_no')::jsonb) FROM variables) 
                OR surface IN (SELECT jsonb_array_elements_text((wheelchair ->> 'surface_no')::jsonb) FROM variables)
                OR (incline_percent IS NOT NULL AND incline_percent > 6))
            )
			OR class_id::text IN (SELECT UNNEST(excluded_class_id_walking) FROM variables)
			OR foot IN (SELECT UNNEST(categories_no_foot) FROM variables)
        THEN 'no'
    ELSE 'unclassified'
    END AS wheelchair_classified
    FROM ways w
    ) x
WHERE w.id = x.id;


--Precalculation of visualized features for lit
DROP TABLE IF EXISTS buffer_lamps;
CREATE TEMP TABLE buffer_lamps as
SELECT ST_BUFFER(way,0.00015,'quad_segs=8') AS geom 
FROM planet_osm_point 
WHERE highway = 'street_lamp';

CREATE INDEX ON buffer_lamps USING gist(geom);


WITH variables AS 
(
    SELECT select_from_variable_container_o('lit') AS lit
)
UPDATE ways w SET lit_classified = x.lit_classified
FROM
    (SELECT w.id,
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
    FROM ways w
    ) x
WHERE w.id = x.id;

UPDATE ways w SET lit_classified = 'yes'
FROM buffer_lamps b
WHERE (lit IS NULL OR lit = '')
AND ST_Intersects(b.geom,w.geom);

--Mark network islands in the network
INSERT INTO osm_way_classes(class_id,name) values(701,'network_island');

DROP TABLE IF EXISTS network_islands; 
CREATE TABLE network_islands AS 
WITH RECURSIVE ways_no_islands AS (
	SELECT id,geom FROM 
	(SELECT id,geom
	FROM ways w
	WHERE w.class_id::text NOT IN (SELECT UNNEST(variable_array) from variable_container WHERE identifier = 'excluded_class_id_walking')
	AND w.class_id::text NOT IN (SELECT UNNEST(variable_array) from variable_container WHERE identifier = 'excluded_class_id_cycling')
	AND (
	(w.foot NOT IN (SELECT UNNEST(variable_array) FROM variable_container WHERE identifier = 'categories_no_foot') OR foot IS NULL)
	OR
	(w.bicycle NOT IN (SELECT UNNEST(variable_array) from variable_container WHERE identifier = 'categories_no_bicycle') OR bicycle IS NULL))
	LIMIT 1) x
	UNION 
	SELECT w.id,w.geom
	FROM ways w, ways_no_islands n
	WHERE ST_Intersects(n.geom,w.geom)
	AND w.class_id::text NOT IN (SELECT UNNEST(variable_array) from variable_container WHERE identifier = 'excluded_class_id_walking')
	AND w.class_id::text NOT IN (SELECT UNNEST(variable_array) from variable_container WHERE identifier = 'excluded_class_id_cycling')
	AND (
	(w.foot NOT IN (SELECT UNNEST(variable_array) FROM variable_container WHERE identifier = 'categories_no_foot') OR foot IS NULL)
	OR
	(w.bicycle NOT IN (SELECT UNNEST(variable_array) from variable_container WHERE identifier = 'categories_no_bicycle') OR bicycle IS NULL)
)  
) 
SELECT w.id  
FROM (
	SELECT w.id
	FROM ways w
	LEFT JOIN ways_no_islands n
	ON w.id = n.id
	WHERE n.id IS null
) x, ways w
WHERE w.id = x.id
AND w.class_id::text NOT IN (SELECT UNNEST(variable_array) from variable_container WHERE identifier = 'excluded_class_id_walking')
AND w.class_id::text NOT IN (SELECT UNNEST(variable_array) from variable_container WHERE identifier = 'excluded_class_id_cycling')
AND (
 	(w.foot NOT IN (SELECT UNNEST(variable_array) FROM variable_container WHERE identifier = 'categories_no_foot') OR foot IS NULL)
	OR
	(w.bicycle NOT IN (SELECT UNNEST(variable_array) from variable_container WHERE identifier = 'categories_no_bicycle') OR bicycle IS NULL)
); 

ALTER TABLE network_island ADD PRIMARY KEY(id);
UPDATE ways w SET class_id = 701
FROM network_islands n
WHERE w.id = n.id; 


ALTER TABLE ways_vertices_pgr ADD COLUMN class_ids int[];
ALTER TABLE ways_vertices_pgr ADD COLUMN foot text[];
ALTER TABLE ways_vertices_pgr ADD COLUMN bicycle text[];
ALTER TABLE ways_vertices_pgr ADD COLUMN lit_classified text[];
ALTER TABLE ways_vertices_pgr ADD COLUMN wheelchair_classified text[];

WITH ways_attributes AS (
	SELECT vv.id, array_remove(array_agg(DISTINCT x.class_id),NULL) class_ids,
	array_remove(array_agg(DISTINCT x.foot),NULL) AS foot,
	array_remove(array_agg(DISTINCT x.bicycle),NULL) bicycle,
	array_remove(array_agg(DISTINCT x.lit_classified),NULL) lit_classified,
	array_remove(array_agg(DISTINCT x.wheelchair_classified),NULL) wheelchair_classified
	FROM ways_vertices_pgr vv
	LEFT JOIN
	(	SELECT v.id, w.class_id, w.foot, w.bicycle, w.lit_classified, w.wheelchair_classified 
		FROM ways_vertices_pgr v, ways w 
		WHERE st_intersects(v.geom,w.geom)
	) x
	ON vv.id = x.id
	GROUP BY vv.id
)
UPDATE ways_vertices_pgr v
SET class_ids = w.class_ids, 
foot = w.foot,
bicycle = w.bicycle,
lit_classified = w.lit_classified,
wheelchair_classified  = w.wheelchair_classified
FROM ways_attributes w
WHERE v.id = w.id;

-- Mark dedicated lanes as foot = 'no'

UPDATE ways w
SET foot = 'no'  FROM ( SELECT osm_id FROM planet_osm_line WHERE highway = 'service' AND (tags->'psv' IS NOT NULL OR tags->'bus' = 'yes') ) x WHERE w.osm_id = x.osm_id;

-- Mark underground cycle lanes as foot = 'no' this is for the specific case of BOG
--UPDATE ways
--SET foot = 'yes' WHERE bicycle != 'no'AND foot = 'no';
--


ALTER TABLE ways ADD COLUMN slope_profile jsonb[];
ALTER TABLE ways ADD COLUMN s_imp NUMERIC;
ALTER TABLE ways ADD COLUMN rs_imp NUMERIC;
--Add slope_profile for ways
DO $$
BEGIN 
	IF to_regclass('public.dem_vec') IS NOT NULL THEN 
		CREATE TEMP TABLE temp_slopes AS
		WITH x AS (
			SELECT compute_ways_slope_bulk(10000) AS slope_json
		)
		SELECT (slope_json[1] ->> 'id') AS id, (slope_json[1] ->> 's_imp') AS s_imp, 
		(slope_json[1] ->> 'rs_imp') AS rs_imp, slope_json[2:] AS slope_profile
		FROM x;

		ALTER TABLE temp_slopes ADD PRIMARY KEY(id);

		UPDATE ways w
		SET slope_profile = t.slope_profile,
		s_imp = t.s_imp::numeric,
		rs_imp = t.rs_imp::numeric
		FROM temp_slopes t 
		WHERE w.id = t.id::bigint;
	END IF;
END
$$;

ALTER TABLE ways ADD COLUMN impedance_surface NUMERIC;
UPDATE ways SET impedance_surface = (select_from_variable_container_o('cycling_surface') ->> surface)::NUMERIC 
WHERE surface IS NOT NULL
AND surface IN(SELECT jsonb_object_keys(select_from_variable_container_o('cycling_surface')));

--Mark vertices that are on network islands
WITH count_ids AS (
	SELECT count(*), source AS id 
	FROM ways
	GROUP by source
	UNION ALL
	SELECT count(*), target AS id
	FROM ways
	GROUP by target
),
only_once AS (
	SELECT c.id,sum(c.count), v.geom 
	FROM count_ids c, ways_vertices_pgr v
	WHERE c.id = v.id
	GROUP by c.id, v.geom
	having sum(count) < 2
),
vertices_islands AS (
	SELECT w.source, w.target
	FROM only_once o, only_once o1, ways w
	WHERE w.source = o.id 
	and w.target = o1.id
),
vertices_to_update AS (
	SELECT x.id
	FROM (
		SELECT source AS id 
		FROM vertices_islands 
		UNION ALL
		SELECT target AS id 
		FROM vertices_islands 
	) x
	, ways_vertices_pgr v
	WHERE v.id = x.id
)
UPDATE ways_vertices_pgr 
SET class_ids = array[0]
FROM vertices_to_update v
WHERE ways_vertices_pgr.id = v.id;

--Identify death_end in the network
DROP TABLE IF EXISTS death_end_v;
CREATE TEMP TABLE death_end_v AS 
WITH death_end AS (
	SELECT count(source),source 
	FROM (
		SELECT SOURCE 
		FROM ways 
		UNION ALL
		SELECT target 
		FROM ways 
	) x
	GROUP BY SOURCE 
	HAVING count(source) = 1
)
SELECT v.*
FROM ways_vertices_pgr v, death_end d
WHERE v.id = d.SOURCE;

ALTER TABLE ways ADD COLUMN death_end BIGINT;

UPDATE ways w SET death_end = w.target  
FROM death_end_v d 
WHERE d.id = w.SOURCE;

UPDATE ways w SET death_end = w.source 
FROM death_end_v d 
WHERE d.id = w.target;

ALTER TABLE ways_vertices_pgr ADD COLUMN death_end BOOLEAN;
CREATE INDEX ON ways_vertices_pgr (death_end);

WITH s AS (
	SELECT w.id,w.geom,w.target vid 
	FROM ways w, death_end_v v
	WHERE w.SOURCE = v.id
	UNION ALL 
	SELECT w.id,w.geom,w.source vid 
	FROM ways w, death_end_v v
	WHERE w.target = v.id
)
UPDATE ways_vertices_pgr v
SET death_end = TRUE
FROM s 
WHERE v.id = s.vid; 

CREATE INDEX ON ways USING btree(foot);
CREATE INDEX ON ways USING btree(id);
CREATE INDEX ON ways_vertices_pgr USING btree(cnt);

CREATE SEQUENCE ways_vertices_pgr_id_seq;
ALTER TABLE ways_vertices_pgr ALTER COLUMN id SET DEFAULT nextval('ways_vertices_pgr_id_seq');
ALTER SEQUENCE ways_vertices_pgr_id_seq OWNED BY ways_vertices_pgr.id;
SELECT setval('ways_vertices_pgr_id_seq', COALESCE(max(id), 0)) FROM ways_vertices_pgr;

CREATE SEQUENCE ways_id_seq;
ALTER TABLE ways ALTER COLUMN id SET DEFAULT nextval('ways_id_seq');
ALTER SEQUENCE ways_id_seq OWNED BY ways.id;
SELECT setval('ways_id_seq', COALESCE(max(id), 0)) FROM ways;

CREATE TABLE ways_userinput (LIKE ways INCLUDING ALL);
INSERT INTO ways_userinput
SELECT * FROM ways;

CREATE TABLE ways_userinput_vertices_pgr (LIKE ways_vertices_pgr INCLUDING ALL);
INSERT INTO ways_userinput_vertices_pgr
SELECT * FROM ways_vertices_pgr;

ALTER TABLE ways_userinput add column userid int4;
ALTER TABLE ways_userinput_vertices_pgr add column userid int4;
ALTER TABLE ways_userinput add column scenario_id int4;
ALTER TABLE ways_userinput_vertices_pgr add column scenario_id int4;
ALTER TABLE ways_userinput ADD COLUMN original_id BIGINT;
CREATE INDEX ON ways_userinput USING btree (userid);
CREATE INDEX ON ways_userinput_vertices_pgr USING btree (userid);
CREATE INDEX ON ways_userinput USING btree (scenario_id);
CREATE INDEX ON ways_userinput_vertices_pgr USING btree (scenario_id);
CREATE INDEX ON ways_userinput (original_id);