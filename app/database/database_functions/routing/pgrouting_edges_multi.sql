CREATE OR REPLACE FUNCTION public.pgrouting_edges_multi(cutoffs double precision[], startpoints double precision[], speed numeric, modus_input integer, routing_profile text, userid_input integer DEFAULT 1, scenario_id_input integer DEFAULT 1)
 RETURNS SETOF void
 LANGUAGE plpgsql
AS $function$
DECLARE 
	vids bigint[];
BEGIN
	
	PERFORM pgrouting_edges_preparation(cutoffs, startpoints, speed, modus_input, routing_profile,userid_input,scenario_id_input);
	
	SELECT ARRAY_AGG(vid)
	INTO vids
	FROM start_vertices s;

	/*Perform routing with multiple starting points*/
	DROP TABLE IF EXISTS reached_edges; 
	CREATE TEMP TABLE reached_edges AS 
	SELECT p.from_v, p.edge, p.start_perc, p.end_perc, greatest(start_cost,end_cost)::smallint AS COST, start_cost::smallint, end_cost::SMALLINT 
	FROM pgr_isochrones(
		'SELECT * FROM temp_fetched_ways', 
		vids, cutoffs, TRUE
	) p;

	CREATE INDEX ON reached_edges (edge);
	DELETE FROM reached_edges WHERE edge IN (SELECT id FROM artificial_edges);
	
	INSERT INTO reached_edges
	SELECT a.source, a.id, 0, 1, a.COST, 0, a.COST
	FROM artificial_edges a, start_vertices v
	WHERE a.SOURCE = v.vid 
	UNION ALL 
	SELECT a.target, a.id, 0, 1, a.reverse_cost, a.reverse_cost, 0
	FROM artificial_edges a, start_vertices v
	WHERE a.target = v.vid; 

	DROP TABLE IF EXISTS multi_edges;
	CREATE TEMP TABLE multi_edges AS 
	WITH full_edges AS 
	(	
		SELECT r.*, w.geom 
		FROM reached_edges r, temp_fetched_ways w 
		WHERE (r.start_perc = 0 
		AND r.end_perc = 1)
		AND r.edge = w.id
	)
	SELECT r.from_v, r.edge, r.cost, r.start_cost, r.end_cost, ST_LineSubstring(r.geom, r.start_perc, r.end_perc) AS geom
	FROM (
		SELECT e.*, w.geom
		FROM reached_edges e, temp_fetched_ways w 
		WHERE e.edge = w.id
		AND (e.start_perc <> 0 OR e.end_perc <> 1) 
	) r
	LEFT JOIN full_edges f
	ON r.edge = f.edge 
	WHERE f.edge IS NULL
	UNION ALL 
	SELECT from_v, edge, COST, start_cost, end_cost, geom
	FROM full_edges; 

	ALTER TABLE multi_edges ADD COLUMN id serial;
	ALTER TABLE multi_edges ADD PRIMARY key(id);
	CREATE INDEX ON multi_edges(cost);
END;
$function$;

/*
SELECT * 
FROM public.pgrouting_edges_multi(ARRAY[300.,600.,900.], ARRAY[[11.2493, 48.1804],[11.2315,48.1778]],1.33, 1,'walking_standard',1,1)
*/