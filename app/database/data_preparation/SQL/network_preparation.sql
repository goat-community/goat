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

/*Split long ways that. Parameter max_length can be set in the variable container*/
DO $$
DECLARE
	max_length integer; 
	excluded_class_id integer[];
	categories_no_foot text[];
BEGIN 
	
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


INSERT INTO osm_way_classes(class_id,name) values(801,'foot_no');
INSERT INTO osm_way_classes(class_id,name) values(701,'network_island');

--Mark network islands in the network

WITH RECURSIVE ways_no_islands AS (
 SELECT id,geom
 FROM ways
 WHERE id = 1
 UNION
 SELECT w.id,w.geom
 FROM ways w, ways_no_islands n
 WHERE ST_Intersects(n.geom,w.geom)
 AND w.class_id::text NOT IN (SELECT UNNEST(variable_array) from variable_container WHERE identifier = 'excluded_class_id_walking')
 AND (w.foot NOT IN (SELECT UNNEST(variable_array) FROM variable_container WHERE identifier = 'categories_no_foot') OR foot IS NULL)  
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
AND ways.class_id::text NOT IN (SELECT unnest(variable_array) from variable_container WHERE identifier = 'excluded_class_id_walking')
AND (
	ways.foot NOT IN (SELECT UNNEST(variable_array) FROM variable_container WHERE identifier = 'categories_no_foot') 
	OR ways.foot IS NULL
); 

ALTER TABLE ways_vertices_pgr ADD COLUMN class_ids int[];
WITH class_ids AS (
	SELECT vv.id, array_agg(DISTINCT x.class_id) class_ids
	FROM ways_vertices_pgr vv
	LEFT JOIN
	(	SELECT v.id,
		CASE WHEN w.foot in(SELECT unnest(variable_array) FROM variable_container WHERE identifier = 'categories_no_foot') 
		THEN 801 ELSE w.class_id END AS class_id 
		FROM ways_vertices_pgr v, ways w 
		WHERE st_intersects(v.geom,w.geom)
	) x
	ON vv.id = x.id
	GROUP BY vv.id
)
UPDATE ways_vertices_pgr SET class_ids = c.class_ids
FROM class_ids c
WHERE ways_vertices_pgr.id = c.id;

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

CREATE INDEX ON ways USING btree(foot);
CREATE INDEX ON ways USING btree(id);
CREATE INDEX ON ways_vertices_pgr USING btree(cnt);

--Precalculation of visualized features for wheelchair
WITH variables AS 
(
    SELECT variable_object AS wheelchair ,
    select_from_variable_container('excluded_class_id_walking') AS excluded_class_id_walking,
    select_from_variable_container('categories_no_foot') AS categories_no_foot,
    select_from_variable_container('categories_sidewalk_no_foot') AS categories_sidewalk_no_foot
    FROM variable_container
    WHERE identifier='wheelchair'
) 
UPDATE ways w SET wheelchair_classified = x.wheelchair_classified
FROM
    (SELECT w.id,
    CASE WHEN 
        wheelchair IN ('yes','Yes') 
        OR ( sidewalk IN ('both','left','right')
            AND (
                sidewalk_both_width >= 1.80 OR sidewalk_left_width >= 1.80 OR sidewalk_right_width >= 1.80
                )
            ) 
        OR (wheelchair IS NULL AND width >= 1.80 AND highway <> 'steps' 
            AND (smoothness IS NULL OR 
            (smoothness NOT IN (SELECT jsonb_array_elements_text((wheelchair ->> 'smoothness_no')::jsonb) FROM variables)
            AND smoothness NOT IN (SELECT jsonb_array_elements_text((wheelchair ->> 'smoothness_limited')::jsonb) FROM variables)
            )
            AND (surface IS NULL OR surface NOT IN (SELECT jsonb_array_elements_text((wheelchair ->> 'surface_no')::jsonb) FROM variables))
            AND (incline_percent IS NULL OR incline_percent < 6)
            ))
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
        THEN 'no'
    ELSE 'unclassified'
    END AS wheelchair_classified
    FROM ways w, study_area s
    WHERE class_id::text NOT IN (SELECT UNNEST(excluded_class_id_walking) FROM variables)
    AND (foot IS NULL OR foot NOT IN (SELECT UNNEST(categories_no_foot) FROM variables))
    ) x
WHERE w.id = x.id
;

--Precalculation of visualized features for lit
WITH variables AS 
(
    SELECT variable_object AS lit ,
    select_from_variable_container('excluded_class_id_walking') AS excluded_class_id_walking,
    select_from_variable_container('categories_no_foot') AS categories_no_foot,
    select_from_variable_container('categories_sidewalk_no_foot') AS categories_sidewalk_no_foot
    FROM variable_container
    WHERE identifier='lit'
)
UPDATE ways w SET lit_classified = x.lit_classified
FROM
    (SELECT w.id,
    CASE WHEN 
        lit IN ('yes','Yes') 
        OR (lit IS NULL AND highway IN (SELECT jsonb_array_elements_text((lit ->> 'highway_yes')::jsonb) FROM variables))
        THEN 'yes' 
    WHEN
        lit IN ('no','No')
        OR (lit IS NULL AND (highway IN (SELECT jsonb_array_elements_text((lit ->> 'highway_no')::jsonb) FROM variables) 
        OR surface IN (SELECT jsonb_array_elements_text((lit ->> 'surface_no')::jsonb) FROM variables))
        )
        THEN 'no'
    ELSE 'unclassified'
    END AS lit_classified 
    FROM ways w, study_area s
    ) x
WHERE w.id = x.id
;

CREATE TABLE ways_userinput (LIKE ways INCLUDING ALL);
INSERT INTO ways_userinput
SELECT * FROM ways;

CREATE TABLE ways_userinput_vertices_pgr (LIKE ways_vertices_pgr INCLUDING ALL);
INSERT INTO ways_userinput_vertices_pgr
SELECT * FROM ways_vertices_pgr;

ALTER TABLE ways_userinput add column userid int4;
ALTER TABLE ways_userinput_vertices_pgr add column userid int4;
CREATE INDEX ON ways_userinput USING btree (userid);
CREATE INDEX ON ways_userinput_vertices_pgr USING btree (userid);

