ALTER TABLE ways
DROP COLUMN RULE,DROP COLUMN x1,DROP COLUMN x2,DROP COLUMN y1,DROP COLUMN y2, DROP COLUMN priority,
DROP COLUMN length,DROP COLUMN cost,DROP COLUMN reverse_cost, DROP COLUMN cost_s, DROP COLUMN reverse_cost_s;
ALTER TABLE ways rename column gid to id;
ALTER TABLE ways rename column the_geom to geom;
ALTER TABLE ways_vertices_pgr rename column the_geom to geom;
ALTER TABLE ways alter column target type int4;
ALTER TABLE ways alter column source type int4;
ALTER TABLE ways 
	ADD COLUMN bicycle_road text, ADD COLUMN bicycle text, ADD COLUMN cycleway text, ADD COLUMN foot text, 
	ADD COLUMN highway text, ADD COLUMN incline text, ADD COLUMN incline_percent integer,
	ADD COLUMN lanes NUMERIC, ADD COLUMN lit text, ADD COLUMN lit_classified text, ADD COLUMN parking text, 
	ADD COLUMN parking_lane_both text, ADD COLUMN parking_lane_right text, ADD COLUMN parking_lane_left text, 
	ADD COLUMN segregated text, ADD COLUMN sidewalk text, ADD COLUMN sidewalk_both_width NUMERIC, 
	ADD COLUMN sidewalk_left_width NUMERIC, ADD COLUMN sidewalk_right_width NUMERIC, ADD COLUMN smoothness text, 
	ADD COLUMN surface text, ADD COLUMN wheelchair text, ADD COLUMN wheelchair_classified text, ADD COLUMN width numeric;


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
SET foot = p.foot, bicycle = p.bicycle
from planet_osm_line p
WHERE ways.osm_id = p.osm_id;

/*There shouldn't be further need for splitting the network
Split long ways that. Parameter max_length can be set in the variable container
DO $$
DECLARE
	max_length integer; 
	excluded_class_id integer[];
	categories_no_foot text[];
BEGIN 
	--We should add cycling here as well
	SELECT select_from_variable_container('excluded_class_id_walking')::integer[],
	select_from_variable_container('categories_no_foot')::text[]
	INTO excluded_class_id, categories_no_foot;
 	
	SELECT variable_simple::integer
	INTO max_length
	FROM variable_container
	WHERE identifier = 'max_length_links';

	WITH splited_ways AS (
		SELECT id,class_id,ST_Length(split_long_way(geom,length_m::NUMERIC,max_length)::geography) AS length_m,
		osm_id, foot,bicycle, split_long_way(geom,length_m::NUMERIC,max_length) AS geom
		FROM ways w
		WHERE length_m > max_length
		AND w.class_id not in (select UNNEST(excluded_class_id))
		AND (foot not in (SELECT UNNEST(categories_no_foot)) OR foot IS NULL)
	),
	delete_old AS (
		DELETE FROM ways w 
		USING splited_ways s 
		WHERE w.id = s.id
	)
	INSERT INTO ways(class_id,length_m,osm_id,foot,bicycle,geom)
	SELECT class_id,length_m, osm_id, foot, bicycle, geom 
	FROM splited_ways;

	UPDATE ways w SET SOURCE = v.id 
	FROM ways_vertices_pgr v 
	WHERE ST_astext(st_startpoint(w.geom)) = ST_astext(v.geom)
	AND SOURCE IS NULL;

	UPDATE ways w SET target = v.id 
	FROM ways_vertices_pgr v 
	WHERE ST_astext(st_endpoint(w.geom)) = ST_astext(v.geom)
	AND target IS null;

	WITH new_vertices AS (
		SELECT st_startpoint(geom) AS geom 
		FROM ways  
		WHERE SOURCE IS NULL 
		UNION ALL 
		SELECT st_endpoint(geom) AS geom 
		FROM ways
		WHERE target IS NULL 
	)
	INSERT INTO ways_vertices_pgr(geom)
	SELECT DISTINCT geom 
	FROM new_vertices; 
	
	UPDATE ways w SET SOURCE = v.id 
	FROM ways_vertices_pgr v 
	WHERE ST_astext(st_startpoint(w.geom)) = ST_astext(v.geom)
	AND SOURCE IS NULL;

	UPDATE ways w SET target = v.id 
	FROM ways_vertices_pgr v 
	WHERE ST_astext(st_endpoint(w.geom)) = ST_astext(v.geom)
	AND target IS null;

END
$$;

*/
UPDATE ways 
SET highway = l.highway, surface = l.surface, 
	width = (CASE WHEN l.width ~ '^[0-9.]*$' THEN l.width::numeric ELSE NULL END)
FROM (select osm_id, highway, surface, width from planet_osm_line p) l
WHERE ways.osm_id = l.osm_id;

UPDATE ways 
SET bicycle_road = l.bicycle_road, cycleway = l.cycleway, incline = l.incline, lit = l.lit, parking = l.parking, 
	parking_lane_both = l.parking_lane_both, parking_lane_right = l.parking_lane_right, 
	parking_lane_left = l.parking_lane_left, segregated = l.segregated,
	sidewalk = l.sidewalk, smoothness = l.smoothness, wheelchair = l.wheelchair
FROM (select osm_id, (tags -> 'bicycle_road') AS bicycle_road, 
	(tags -> 'cycleway') AS cycleway, 
	(tags -> 'incline') AS incline, (tags -> 'lit') AS lit, 
	(tags -> 'parking') AS parking, (tags -> 'parking:lane:both') AS parking_lane_both, 
	(tags -> 'parking:lane:right') AS parking_lane_right, 
	(tags -> 'parking:lane:left') AS parking_lane_left,
	(tags -> 'segregated') AS segregated, 
	(tags -> 'sidewalk') AS sidewalk, 
	(tags -> 'smoothness') AS smoothness,
	(tags -> 'wheelchair') AS wheelchair
	from planet_osm_line p) l
WHERE ways.osm_id = l.osm_id;

UPDATE ways
SET incline_percent=xx.incline_percent::integer 
FROM (
	SELECT id, regexp_REPLACE(incline,'[^0-9]+','','g') AS incline_percent
	FROM ways
) xx 
WHERE xx.incline_percent IS NOT NULL AND xx.incline_percent <> '' 
AND ways.id = xx.id;

UPDATE ways 
SET lanes = l.lanes::numeric
FROM (select p.*, (tags -> 'lanes') as lanes from planet_osm_line p) l
WHERE ways.osm_id = l.osm_id;

UPDATE ways 
SET sidewalk_both_width = l.sidewalk_both_width::numeric
FROM (select p.*, (tags -> 'sidewalk:both:width') as sidewalk_both_width from planet_osm_line p) l
WHERE ways.osm_id = l.osm_id;

UPDATE ways 
SET sidewalk_left_width = l.sidewalk_left_width::numeric
FROM (select p.*, (tags -> 'sidewalk:left:width') as sidewalk_left_width from planet_osm_line p) l
WHERE ways.osm_id = l.osm_id;

UPDATE ways 
SET sidewalk_right_width = l.sidewalk_right_width::numeric
FROM (select p.*, (tags -> 'sidewalk:right:width') as sidewalk_right_width from planet_osm_line p) l
WHERE ways.osm_id = l.osm_id;

--Updating default speed limits for living_streets
UPDATE ways
SET maxspeed_forward = 7
WHERE highway = 'living_street' AND maxspeed_forward = 50;

UPDATE ways
SET maxspeed_backward = 7
WHERE highway = 'living_street' AND maxspeed_backward = 50;

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
CREATE TABLE buffer_lamps as
SELECT ST_BUFFER(way,0.00015,'quad_segs=8') AS geom 
FROM planet_osm_point 
WHERE highway = 'street_lamp';

CREATE INDEX ON buffer_lamps USING gist(geom);


WITH variables AS 
(
    SELECT select_from_variable_container_o('lit') AS lit,
    select_from_variable_container('excluded_class_id_walking') AS excluded_class_id_walking,
    select_from_variable_container('categories_no_foot') AS categories_no_foot,
    select_from_variable_container('categories_sidewalk_no_foot') AS categories_sidewalk_no_foot
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

WITH RECURSIVE ways_no_islands AS (
	SELECT id,geom
	FROM ways
	WHERE id = 1
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
UPDATE ways SET class_id = 701 
FROM (
	SELECT w.id
	FROM ways w
	LEFT JOIN ways_no_islands n
	ON w.id = n.id
	WHERE n.id IS null
) x
WHERE ways.id = x.id
AND ways.class_id::text NOT IN (SELECT UNNEST(variable_array) from variable_container WHERE identifier = 'excluded_class_id_walking')
AND ways.class_id::text NOT IN (SELECT UNNEST(variable_array) from variable_container WHERE identifier = 'excluded_class_id_cycling')
AND (
 	(ways.foot NOT IN (SELECT UNNEST(variable_array) FROM variable_container WHERE identifier = 'categories_no_foot') OR foot IS NULL)
	OR
	(ways.bicycle NOT IN (SELECT UNNEST(variable_array) from variable_container WHERE identifier = 'categories_no_bicycle') OR bicycle IS NULL)
); 

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
ALTER TABLE ways_userinput ADD COLUMN original_id BIGINT;
CREATE INDEX ON ways_userinput USING btree (userid);
CREATE INDEX ON ways_userinput_vertices_pgr USING btree (userid);
CREATE INDEX ON ways_userinput (original_id);

