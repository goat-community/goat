CREATE OR REPLACE FUNCTION public.pgrouting_edges_heatmap(cutoffs double precision[], startpoints double precision[], speed numeric, gridid_input integer[], modus_input integer, routing_profile text, userid_input integer DEFAULT 0, scenario_id_input integer DEFAULT 0, section_id_input integer DEFAULT 0)
 RETURNS SETOF void
 LANGUAGE plpgsql
AS $function$
DECLARE 
	vids bigint[];
BEGIN
	
	PERFORM pgrouting_edges_preparation(cutoffs, startpoints, speed, modus_input, routing_profile,userid_input,scenario_id_input,TRUE);

	SELECT ARRAY_AGG(vid)
	INTO vids
	FROM start_vertices s
	WHERE s.section_id = section_id_input; 

	/*Perform routing with multiple starting points*/
	DROP TABLE IF EXISTS reached_edges; 
	CREATE TEMP TABLE reached_edges AS 
	SELECT s.grid_id, p.from_v, p.edge, p.start_perc, p.end_perc, start_cost::SMALLINT, end_cost::SMALLINT 
	FROM pgr_isochrones(
		'SELECT * FROM temp_fetched_ways', 
		vids, cutoffs
	) p, start_vertices s 
	WHERE p.from_v = s.vid
	AND s.section_id = section_id_input;

	/*Cleaning artificial edges*/
	CREATE INDEX ON reached_edges (edge);
	DELETE FROM reached_edges r
	USING artificial_edges a 
	WHERE edge = a.id
	AND (r.from_v = a.SOURCE OR r.from_v = a.target);

	INSERT INTO reached_edges
	SELECT v.grid_id, a.source, a.id, 0, 1, 0, a.COST
	FROM artificial_edges a, start_vertices v
	WHERE a.SOURCE = v.vid 
	AND v.section_id = section_id_input
	UNION ALL 
	SELECT v.grid_id, a.target, a.id, 0, 1, a.reverse_cost, 0
	FROM artificial_edges a, start_vertices v
	WHERE a.target = v.vid
	AND v.section_id = section_id_input; 	
	
	DROP TABLE IF EXISTS grouped_edges;
	CREATE TEMP TABLE grouped_edges AS 
	SELECT r.edge, array_agg(r.grid_id) gridids,array_agg(r.start_cost) start_cost, array_agg(r.end_cost) end_cost   
	FROM reached_edges r  
	WHERE (start_perc = 0 AND end_perc = 1)
	GROUP BY edge;  
	
	ALTER TABLE grouped_edges ADD PRIMARY KEY(edge);

	DROP TABLE IF EXISTS full_edges;
	CREATE TEMP TABLE full_edges AS 
	SELECT g.edge, g.gridids, g.start_cost, g.end_cost, userid_input userid, scenario_id_input scenario_id, w.geom, FALSE AS partial_edge
	FROM grouped_edges g, temp_fetched_ways w 
	WHERE g.edge = w.id;

	ALTER TABLE full_edges ADD PRIMARY KEY(edge);
	
	IF (SELECT count(*) FROM reached_edges_heatmap LIMIT 1) = 0 THEN 
		INSERT INTO reached_edges_heatmap(edge, gridids, start_cost, end_cost, userid, scenario_id, geom, partial_edge)
		SELECT f.edge, f.gridids, f.start_cost, f.end_cost, f.userid, f.scenario_id, f.geom, f.partial_edge 
		FROM full_edges f;
	ELSE 	
		/*Add full edges from other batch calculation if same edge_id*/
		UPDATE reached_edges_heatmap r 
		SET gridids = r.gridids || f.gridids, start_cost = r.start_cost || f.start_cost, end_cost = r.end_cost || f.end_cost
		FROM full_edges f
		WHERE f.edge = r.edge
		AND r.partial_edge = FALSE
		AND r.scenario_id = scenario_id_input
		AND r.userid = userid_input;
	
		INSERT INTO reached_edges_heatmap(edge,gridids,start_cost,end_cost,userid,scenario_id,geom, partial_edge)
		SELECT f.*
		FROM full_edges f
		LEFT JOIN 
		(
			SELECT edge 
			FROM reached_edges_heatmap 
			WHERE partial_edge = FALSE
			AND scenario_id = scenario_id_input
			AND userid = userid_input
		) r 
		ON f.edge = r.edge
		WHERE r.edge IS NULL;
	END IF;

	INSERT INTO reached_edges_heatmap(edge,gridids,start_cost,end_cost,userid,scenario_id,geom, start_perc, end_perc, partial_edge)
	SELECT p.edge, array[p.gridids], array[p.start_cost], array[p.end_cost],userid_input, scenario_id_input, geom, start_perc, end_perc, TRUE 
	FROM
	(
		SELECT r.edge, r.grid_id AS gridids, r.start_cost start_cost, r.end_cost end_cost, ST_LINESUBSTRING(w.geom, r.start_perc, r.end_perc) geom, 
		r.start_perc, r.end_perc
		FROM reached_edges r, temp_fetched_ways w  
		WHERE (r.start_perc <> 0 OR r.end_perc <> 1)
		AND r.edge = w.id
	) p;

END;
$function$;

/*
SELECT public.pgrouting_edges_heatmap(ARRAY[1200.], array_agg(starting_points) , 
1.33, array_agg(grid_id)::integer[], 1, 'walking_standard',0,0, 200)
FROM (SELECT * FROM grid_ordered WHERE id BETWEEN 201 AND 400) g
*/

