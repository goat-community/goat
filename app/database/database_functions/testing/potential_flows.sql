DROP FUNCTION IF EXISTS potential_pedestrian_flows;
CREATE OR REPLACE FUNCTION public.potential_pedestrian_flows(x float, y float, userid_input integer, scenario_id_input integer)
RETURNS TABLE (edge_out integer, persons_out integer, geom_out geometry)
AS $function$
DECLARE 
	objectid_input integer := random_between(1,900000000);	
BEGIN 
	PERFORM public.pgrouting_edges_potential_flows(ARRAY[600.], ARRAY[[x,y]],1.33, userid_input, scenario_id_input, objectid_input, 1, 'walking_standard');

	DROP TABLE IF EXISTS raw_flows; 
	CREATE TEMP TABLE raw_flows AS 
	WITH convex AS 
	(
		SELECT ST_CONVEXHULL(ST_COLLECT(e.geom)) AS geom
		FROM edges_potential_flows e
		WHERE e.objectid = objectid_input
	), 
	flows AS 
	(
		SELECT ed.*, SUM(p.persons) AS persons
		FROM persons p
		CROSS JOIN LATERAL
		(
		    SELECT e.edge, e.geom, e.SOURCE, e.target, e.start_cost, e.end_cost, e.cost
		    FROM edges_potential_flows e
		    WHERE e.geom && ST_BUFFER(p.geom,0.0009)
		    AND e.objectid = objectid_input
		    ORDER BY ST_CLOSESTPOINT(e.geom,p.geom) <-> p.geom
		    LIMIT 1           
		) AS ed
		WHERE ST_Intersects(p.geom,(SELECT geom FROM convex))
		GROUP BY ed.edge, ed.geom, ed.SOURCE, ed.target, ed.start_cost, ed.end_cost, ed.cost
	)
	SELECT e.edge, e.geom, e.SOURCE,e.target,e.start_cost, e.end_cost, e.COST, 0 AS persons
	FROM edges_potential_flows e
	LEFT JOIN flows f 
	ON e.edge = f.edge 
	WHERE f.edge IS NULL 
	AND e.objectid = objectid_input
	UNION ALL 
	SELECT * 
	FROM flows;
	
	CREATE INDEX ON raw_flows(edge);

	DROP TABLE IF EXISTS cnt_source_target;
	CREATE TEMP TABLE cnt_source_target AS 
	SELECT sum(cnt), node
	FROM 
	(
		SELECT count(source) AS cnt, SOURCE AS node 
		FROM raw_flows
		WHERE SOURCE <> 0
		GROUP BY SOURCE 
		UNION ALL 
		SELECT count(target), target 
		FROM raw_flows
		WHERE target <> 0
		GROUP BY target
	) x
	GROUP BY node; 
	
	ALTER TABLE cnt_source_target ADD PRIMARY KEY(node);
	ALTER TABLE raw_flows ADD COLUMN start_edge boolean;
	
	UPDATE raw_flows t SET start_edge = TRUE 
	FROM (
		SELECT edge 
		FROM raw_flows
		WHERE SOURCE = 0 OR target = 0
	) x
	WHERE t.edge = x.edge;
	
	UPDATE raw_flows t SET start_edge = TRUE 
	FROM (
		SELECT f.edge 
		FROM cnt_source_target c, raw_flows f
		WHERE (c.node = f.SOURCE OR c.node = f.target) 
		AND c.sum = 1
	) x
	WHERE t.edge = x.edge;
	
	
	DROP TABLE IF EXISTS sequences_flows;
	CREATE TEMP TABLE sequences_flows (edge integer,persons integer);
	
	INSERT INTO sequences_flows
	SELECT cp.* 
	FROM  raw_flows f, LATERAL compute_sequence_stream(edge) cp 
	
	
	
	WHERE f.start_edge IS TRUE;
	
	RETURN query 
	WITH sum_sequences AS 
	(
		SELECT edge, sum(persons) persons
		FROM sequences_flows
		GROUP BY edge 
	)
	SELECT f.edge, (COALESCE(f.persons,0) + COALESCE(s.persons,0))::integer AS persons, f.geom 
	FROM raw_flows f  
	LEFT JOIN sum_sequences s 
	ON f.edge = s.edge;

END;
$function$ LANGUAGE plpgsql;

/*
DROP TABLE flows_testing;
CREATE TABLE flows_testing AS 
SELECT * FROM potential_pedestrian_flows(11.5305, 48.1907, 1, 1)
*/


DELETE FROM edges_potential_flows 

DROP TABLE test3;
CREATE TABLE test3 AS 
SELECT * FROM potential_pedestrian_flows(11.5549, 48.2134, 1, 1)



WITH sum_sequences AS 
(
	SELECT edge, sum(persons) persons
	FROM sequences_flows
	GROUP BY edge 
)
SELECT f.edge, (COALESCE(f.persons,0) + COALESCE(s.persons,0))::integer AS persons, f.geom 
FROM raw_flows f  
LEFT JOIN sum_sequences s 
ON f.edge = s.edge;

CREATE TABLE s_flows AS 
SELECT s.*, r.geom  
FROM sequences_flows s, raw_flows r 
WHERE s.edge = r.edge

DROP TABLE raw_flows 

CREATE TEMP TABLE raw_flows(edge integer, start_cost float, end_cost float, COST float, persons integer);

DROP FUNCTION IF EXISTS compute_sequence_stream;
CREATE OR REPLACE FUNCTION compute_sequence_stream(edge_id integer)
  RETURNS TABLE(edge integer, persons integer) AS
$func$
	WITH RECURSIVE sequence_link AS (
		SELECT edge, start_cost, end_cost, COST, persons
		FROM raw_flows x
		WHERE edge = edge_id
		UNION
		SELECT t.edge, t.start_cost, t.end_cost, t.COST, s.persons 
		FROM raw_flows t, sequence_link s
		WHERE least(s.start_cost,s.end_cost) = t.cost
	) 
	SELECT edge, persons::integer
	FROM sequence_link;

$func$  LANGUAGE sql;


DROP FUNCTION IF EXISTS compute_sequence_stream_new;
CREATE OR REPLACE FUNCTION compute_sequence_stream_new(id_input integer)
  RETURNS TABLE(predecessor integer, edge integer, persons integer, sum_persons integer) AS
$func$
	WITH RECURSIVE sequence_link AS (
		SELECT edge AS predecessor, edge, start_cost, end_cost, COST, persons, persons AS sum_persons
		FROM raw_flows x
		WHERE id = id_input
		UNION
		SELECT s.edge predecessor, t.edge, t.start_cost, t.end_cost, t.COST, t.persons, s.sum_persons + t.persons AS sum_persons
		FROM raw_flows t, sequence_link s
		WHERE least(s.start_cost,s.end_cost) = t.COST
	) 
	SELECT predecessor, edge, persons::integer, sum_persons::integer
	FROM sequence_link;

$func$  LANGUAGE sql;



SELECT * FROM raw_flows WHERE edge = 3599

22

DELETE FROM test_sequences 

CREATE TABLE test_sequences(edge integer,person integer, sum_persons integer);

INSERT INTO test_sequences 
SELECT * 
FROM compute_sequence_stream(3598)

SELECT * 
FROM compute_sequence_stream(3519)

SELECT * FROM test_sequences 

ALTER TABLE raw_flows ADD COLUMN id serial;	


SELECT * FROM raw_flows WHERE edge = 3519

DROP FUNCTION IF EXISTS potential_pedestrian_flows;
CREATE OR REPLACE FUNCTION public.sum_up_flows()
RETURNS SETOF VOID --TABLE (edge_out integer, persons_out integer, geom_out geometry)
AS $function$
DECLARE 

BEGIN 
	
	SELECT * FROM raw_flows WHERE id = 1186;
	
	CREATE TABLE start_edges AS 
	SELECT * FROM raw_flows WHERE start_edge = TRUE;
	

	SELECT *  
	FROM compute_sequence_stream(1186)

END;
$function$ LANGUAGE plpgsql;



