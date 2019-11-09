ALTER TABLE ways
DROP COLUMN RULE,DROP COLUMN x1,DROP COLUMN x2,DROP COLUMN y1,DROP COLUMN y2, DROP COLUMN priority
DROP COLUMN length,DROP COLUMN cost,DROP COLUMN reverse_cost, DROP COLUMN cost_s, DROP COLUMN reverse_cost_s;
ALTER TABLE ways rename column gid to id;
ALTER TABLE ways rename column the_geom to geom;
ALTER TABLE ways_vertices_pgr rename column the_geom to geom;
ALTER TABLE ways alter column target type int4;
ALTER TABLE ways alter column source type int4;
ALTER TABLE ways ADD COLUMN bicycle text;
ALTER TABLE ways ADD COLUMN foot text;
ALTER TABLE ways ADD COLUMN highway text;
ALTER TABLE ways ADD COLUMN incline text;
ALTER TABLE ways ADD COLUMN lanes numeric;
ALTER TABLE ways ADD COLUMN lit text;
ALTER TABLE ways ADD COLUMN parking text;
ALTER TABLE ways ADD COLUMN segregated text;
ALTER TABLE ways ADD COLUMN sidewalk text;
ALTER TABLE ways ADD COLUMN sidewalk_both_width numeric;
ALTER TABLE ways ADD COLUMN sidewalk_left_width numeric;
ALTER TABLE ways ADD COLUMN sidewalk_right_width numeric;
ALTER TABLE ways ADD COLUMN smoothness text;
ALTER TABLE ways ADD COLUMN surface text;
ALTER TABLE ways ADD COLUMN wheelchair text;
ALTER TABLE ways ADD COLUMN width text;


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
SET foot = p.foot, bicycle = p.bicycle, highway = p.highway, surface = p.surface, width = p.width
FROM planet_osm_line p 
WHERE ways.osm_id = p.osm_id;

UPDATE ways 
SET incline = (tags -> 'incline')
FROM planet_osm_line p
WHERE ways.osm_id = p.osm_id;

UPDATE ways 
SET lanes = l.lanes::numeric
FROM (select p.*, (tags -> 'lanes') as lanes from planet_osm_line p) l
WHERE ways.osm_id = l.osm_id;

UPDATE ways 
SET lit = (tags -> 'lit')
FROM planet_osm_line p
WHERE ways.osm_id = p.osm_id;

UPDATE ways 
SET parking = (tags -> 'parking')
FROM planet_osm_line p
WHERE ways.osm_id = p.osm_id;

UPDATE ways 
SET segregated = (tags -> 'segregated')
FROM planet_osm_line p
WHERE ways.osm_id = p.osm_id;

UPDATE ways 
SET sidewalk = (tags -> 'sidewalk')
FROM planet_osm_line p
WHERE ways.osm_id = p.osm_id;

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
FROM (select p.*, (tags -> 'sidewalk:right:width') as sidewalk_bright_width from planet_osm_line p) l
WHERE ways.osm_id = l.osm_id;

UPDATE ways 
SET smoothness = (tags -> 'smoothness')
FROM planet_osm_line p
WHERE ways.osm_id = p.osm_id;

UPDATE ways 
SET wheelchair = (tags -> 'wheelchair')
FROM planet_osm_line p
WHERE ways.osm_id = p.osm_id;



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
		SELECT id, class_id,ST_Length(split_long_way(geom,length_m::NUMERIC,max_length)::geography) AS length_m,
		osm_id, foot, bicycle, split_long_way(geom,length_m::NUMERIC,max_length) AS geom
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



