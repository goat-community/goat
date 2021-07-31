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


