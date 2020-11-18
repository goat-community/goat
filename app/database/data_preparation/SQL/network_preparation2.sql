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