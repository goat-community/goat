DROP FUNCTION IF EXISTS pgrouting_edges_heatmap;
CREATE OR REPLACE FUNCTION public.pgrouting_edges_heatmap(cutoffs float[], startpoints float[][], speed numeric, userid_input integer, scenario_id_input integer, gridid_input integer[], modus_input integer, routing_profile text, count_grids integer DEFAULT 0)
 RETURNS SETOF void
 LANGUAGE plpgsql
AS $function$
DECLARE 
	buffer text;
	distance numeric;
	number_calculation_input integer;
	vids bigint[];
BEGIN
	
	SELECT *
	INTO vids
	FROM pgrouting_edges_preparation(cutoffs, startpoints, speed, userid_input, modus_input, routing_profile, count_grids);

	DROP TABLE IF EXISTS reached_edges; 

	CREATE TEMP TABLE reached_edges AS 
	SELECT gridid_input[999999999-count_grids-p.from_v], p.from_v, p.edge, p.start_perc, p.end_perc, start_cost::SMALLINT, end_cost::SMALLINT 
	FROM pgr_isochrones(
		'SELECT * FROM temp_fetched_ways WHERE id NOT IN(SELECT wid FROM start_vertices)', 
		vids, cutoffs,TRUE
	) p;
	
	DROP TABLE IF EXISTS grouped_edges;
	CREATE TEMP TABLE grouped_edges AS 
	SELECT r.edge, array_agg(r.gridid_input) gridids,array_agg(r.start_cost) start_cost, array_agg(r.end_cost) end_cost   
	FROM reached_edges r  
	WHERE (start_perc = 0 AND end_perc = 1)
	GROUP BY edge;  
	
	ALTER TABLE grouped_edges ADD PRIMARY KEY(edge);

	DROP TABLE IF EXISTS full_edges;
	CREATE TEMP TABLE full_edges AS 
	SELECT g.edge, g.gridids, g.start_cost, g.end_cost, userid_input, scenario_id_input scenario_id, w.geom, FALSE AS partial_edge
	FROM grouped_edges g, temp_fetched_ways w 
	WHERE g.edge = w.id;

	ALTER TABLE full_edges ADD PRIMARY KEY(edge);

	IF (SELECT count(*) FROM reached_edges_heatmap LIMIT 1) = 0 THEN 
		INSERT INTO reached_edges_heatmap(edge, gridids, start_cost, end_cost, userid, scenario_id, geom, partial_edge)
		SELECT f.edge, f.gridids, f.start_cost, f.end_cost, f.userid_input, f.scenario_id, f.geom, f.partial_edge 
		FROM full_edges f;
	ELSE 	
		UPDATE reached_edges_heatmap r 
		SET gridids = r.gridids || f.gridids, start_cost = r.start_cost || f.start_cost, end_cost = r.end_cost || f.end_cost
		FROM full_edges f
		WHERE f.edge = r.edge
		AND r.partial_edge = FALSE;
	
		INSERT INTO reached_edges_heatmap
		SELECT f.*
		FROM full_edges f
		LEFT JOIN (SELECT edge FROM reached_edges_heatmap WHERE partial_edge = FALSE) r 
		ON f.edge = r.edge
		WHERE r.edge IS NULL;
	
	END IF;
	
	INSERT INTO reached_edges_heatmap(edge,gridids,start_cost,end_cost,userid,scenario_id,geom, partial_edge)
	SELECT p.edge, array[p.gridids], array[p.start_cost], array[p.end_cost],userid_input, scenario_id_input, geom, TRUE 
	FROM
	(
		SELECT r.edge, r.gridid_input AS gridids, r.start_cost start_cost, r.end_cost end_cost, ST_LINESUBSTRING(w.geom, r.start_perc, r.end_perc) geom
		FROM reached_edges r, temp_fetched_ways w  
		WHERE (r.start_perc <> 0 OR r.end_perc <> 1)
		AND r.edge = w.id
	) p 
	LEFT JOIN grouped_edges g
	ON p.edge = g.edge
	WHERE g.edge IS NULL;

END;
$function$;
/*
SELECT public.pgrouting_edges_heatmap(ARRAY[1200.], array_agg(starting_points) , 
1.33, 1, 2000, array_agg(grid_id)::integer[], 1, 'walking_standard')
FROM (SELECT * FROM grid_ordered 
LIMIT 5) g


DROP TABLE test 

CREATE TABLE test AS 
SELECT objectids # 311,GREATEST(start_cost[objectids # 311],end_cost[objectids # 311]), geom      
FROM union_edges  
WHERE objectids && ARRAY[311]
*/
/*
1. Update with latest routing function
2. Add artificial edges
3. Allow scenario building 
4. Compute isochrones
5. Improve multi-point-closest-vertex calculation
*/