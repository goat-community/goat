DROP FUNCTION IF EXISTS pgrouting_edges_potential_flows;
CREATE OR REPLACE FUNCTION public.pgrouting_edges_potential_flows(cutoffs float[], startpoints float[][], speed numeric, userid_input integer, scenario_id_input integer, objectid_input integer, modus_input integer, routing_profile text)
 RETURNS SETOF void
 LANGUAGE plpgsql
AS $function$
DECLARE 
	buffer text;
	distance numeric;
	number_calculation_input integer;
	vids bigint[];
BEGIN
	
	PERFORM pgrouting_edges_preparation(cutoffs, startpoints, speed, modus_input, routing_profile, userid_input, scenario_id_input);

	SELECT ARRAY[vid]
	INTO vids
	FROM start_vertices; 

	IF modus_input <> 3 AND array_length(startpoints,1) = 1 THEN 
		SELECT count(objectid) + 1 
    	INTO number_calculation_input
		FROM starting_point_isochrones
		WHERE userid = userid_input; 
		INSERT INTO starting_point_isochrones(userid,geom,objectid,number_calculation)
		SELECT userid_input, closest_point, objectid_input, number_calculation_input
		FROM start_vertices; 
	END IF; 

	DROP TABLE IF EXISTS reached_edges; 

	CREATE TEMP TABLE reached_edges AS 
	SELECT p.from_v, p.edge, p.start_perc, p.end_perc, greatest(start_cost,end_cost) AS COST, start_cost, end_cost, w.SOURCE, w.target, w.geom
	FROM pgr_isochrones(
		'SELECT * FROM temp_fetched_ways', 
		vids, cutoffs,TRUE
	) p, temp_fetched_ways w
	WHERE p.edge = w.id;

	CREATE INDEX ON reached_edges (edge);
	DELETE FROM reached_edges WHERE edge IN (SELECT id FROM artificial_edges);
	
	INSERT INTO reached_edges
	SELECT a.source, a.id, 0, 1, a.COST, 0, a.COST, a.SOURCE, a.target, a.geom 
	FROM artificial_edges a, start_vertices v
	WHERE a.SOURCE = v.vid 
	UNION ALL 
	SELECT a.target, a.id, 0, 1, a.reverse_cost, a.reverse_cost, 0, a.SOURCE, a.target, a.geom 
	FROM artificial_edges a, start_vertices v
	WHERE a.target = v.vid; 

	INSERT INTO edges_potential_flows (edge,COST, start_cost, end_cost, SOURCE, target, geom, objectid)
	WITH full_edges AS 
	(	
		SELECT * 
		FROM reached_edges 
		WHERE (start_perc = 0 
		AND end_perc = 1)
	)
	SELECT r.edge, r.cost, r.start_cost, r.end_cost, 
	CASE WHEN r.start_perc <> 0 THEN 0 ELSE r.SOURCE END AS SOURCE,
	CASE WHEN r.end_perc <> 1 THEN 0 ELSE r.target END AS target, 
	ST_LineSubstring(r.geom, r.start_perc, r.end_perc), objectid_input   
	FROM reached_edges r
	LEFT JOIN full_edges f
	ON r.edge = f.edge 
	WHERE (r.start_perc <> 0 OR r.end_perc <> 1) 
	AND f.edge IS NULL
	UNION ALL 
	SELECT edge, COST, start_cost, end_cost, SOURCE, target, geom, objectid_input 
	FROM full_edges; 
	
END;
$function$;

/*
SELECT * 
FROM public.pgrouting_edges_potential_flows(ARRAY[600.], ARRAY[[11.5197,48.1929]],4.1, 1, 1, 15, 1, 'walking_standard')
*/
