ALTER TABLE ways
DROP COLUMN RULE,DROP COLUMN x1,DROP COLUMN x2,DROP COLUMN y1,DROP COLUMN y2;
ALTER TABLE ways rename column gid to id;
ALTER TABLE ways rename column the_geom to geom;
ALTER TABLE ways_vertices_pgr rename column the_geom to geom;
ALTER TABLE ways alter column target type int4;
ALTER TABLE ways alter column source type int4;
ALTER TABLE ways ADD COLUMN foot text;
ALTER TABLE ways ADD COLUMN bicycle text;

UPDATE ways 
SET foot = p.foot, bicycle = p.bicycle
FROM planet_osm_line p 
WHERE ways.osm_id = p.osm_id;

--INSERT INTO osm_way_classes(class_id,name) values(501,'secondary_use_sidepath');
--INSERT INTO osm_way_classes(class_id,name) values(502,'secondary_link_use_sidepath');
--INSERT INTO osm_way_classes(class_id,name) values(503,'tertiary_use_sidepath');
--INSERT INTO osm_way_classes(class_id,name) values(504,'tertiary_link_use_sidepath');
INSERT INTO osm_way_classes(class_id,name) values(801,'foot_no');
INSERT INTO osm_way_classes(class_id,name) values(701,'network_island');

/*
WITH links_to_UPDATE as (
	SELECT osm_id, o.class_id 
	FROM planet_osm_line p, osm_way_classes o
	WHERE highway in('secondary','secondary_link','tertiary','tertiary_link')
	AND foot = 'use_sidepath'
	AND concat(highway,'_use_sidepath') = o.name
)
UPDATE ways SET class_id = l.class_id
FROM links_to_UPDATE l
WHERE ways.osm_id = l.osm_id;


WITH links_to_UPDATE as (
	SELECT osm_id, o.class_id 
	FROM planet_osm_line p, osm_way_classes o
	WHERE highway in('secondary','secondary_link','tertiary','tertiary_link')
	AND foot = 'use_sidepath'
	AND concat(highway,'_use_sidepath') = o.name
)
UPDATE ways SET class_id = l.class_id
FROM links_to_UPDATE l
WHERE ways.osm_id = l.osm_id;

WITH links_to_UPDATE as (
	SELECT osm_id
	FROM planet_osm_line p
	WHERE foot = 'yes'
)
UPDATE ways SET class_id = 601
FROM links_to_UPDATE l
WHERE ways.osm_id = l.osm_id;

WITH links_to_UPDATE as (
	SELECT osm_id, o.class_id 
	FROM planet_osm_line p, osm_way_classes o
	WHERE highway in('secondary','secondary_link','tertiary','tertiary_link')
	AND foot = 'use_sidepath'
	AND concat(highway,'_use_sidepath') = o.name
)
UPDATE ways SET class_id = l.class_id
FROM links_to_UPDATE l
WHERE ways.osm_id = l.osm_id;


WITH class_id as (
	SELECT unnest(variable_array) class_id
	FROM variable_container 
	WHERE identifier = 'excluded_class_id_walking'
),
class_names as(
	SELECT c.class_id, o.name
	FROM class_id c, osm_way_classes o
	WHERE c.class_id::integer = o.class_id
	AND c.class_id::integer < 500
),
links_to_UPDATE as(
	SELECT osm_id
	FROM planet_osm_line p, class_names c
	WHERE p.highway = c.name
	AND foot = 'yes'
	UNION ALL
	SELECT osm_id
	FROM planet_osm_line p
	WHERE (tags -> 'sidewalk') IS NOT NULL
	AND (tags -> 'sidewalk') <> 'no'
	AND (tags -> 'sidewalk') <> 'none'
)
UPDATE ways SET class_id = 601
FROM links_to_UPDATE l
WHERE ways.osm_id = l.osm_id;
*/
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

CREATE INDEX ON ways USING btree(foot);


