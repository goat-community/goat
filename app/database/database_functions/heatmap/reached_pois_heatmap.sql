
DROP FUNCTION IF EXISTS reached_pois_heatmap;
CREATE OR REPLACE FUNCTION public.reached_pois_heatmap(buffer_geom geometry, snap_distance NUMERIC, combination_scenarios text DEFAULT 'default', scenario_id_input integer DEFAULT 0)
RETURNS VOID
AS $function$
DECLARE
	sensitivities integer[] := select_from_variable_container('heatmap_sensitivities');
	series_sensitivities integer[]; 
	scenario_edges integer := 0;
	scenario_pois integer := 0;
	cnt_scenario_edges integer; 
	buffer_edges geometry; 
	buffer_pois geometry;
BEGIN 
	
	SELECT count(*) 
	INTO cnt_scenario_edges
	FROM 
	(
		SELECT *
		FROM reached_edges_heatmap 
		WHERE scenario_id = scenario_id_input 
		AND ST_Intersects(geom, buffer_geom) LIMIT 1
	) x;
	
	buffer_edges = ST_BUFFER(buffer_geom,0.0014);
	buffer_pois = buffer_geom;
	
	/*This is preliminary. We need a better way for handling the scenarios. */
	IF combination_scenarios = 'default' THEN /*No Scenario*/
		scenario_edges = 0;
		scenario_pois = 0;
		RAISE NOTICE '%',scenario_edges;
	ELSEIF combination_scenarios = 'scenario' /*POIs and edges scenario*/ AND cnt_scenario_edges > 0 THEN 
		scenario_edges = scenario_id_input;
		scenario_pois = scenario_id_input;
		buffer_pois = buffer_edges;
	ELSE  /*Only pois scenario*/
		scenario_edges = 0;
		scenario_pois = scenario_id_input;
		RAISE NOTICE '%', scenario_pois;
	END IF; 

	series_sensitivities = (SELECT array_agg(x.s)
	FROM (SELECT generate_series(1,ARRAY_LENGTH(select_from_variable_container('heatmap_sensitivities'),1)) s) x);
	/*Match all POIs that have their closest distance to an full edge*/
	DROP TABLE IF EXISTS reached_full_edges;


	/*Potential for performance improvements
	 - Run cross join on smaller set of edges by removing unchanged edges
	 - reduce number of POIs checked
	 - experiment with buffer distance
	 - rewrite interpolate_cost in C
	*/

	CREATE TEMP TABLE reached_full_edges AS 
	WITH p AS 
    (
        SELECT p.gid, p.amenity, p.name, p.geom, e.edge, e.gridids, e.fraction, e.start_cost, e.end_cost
        FROM pois_userinput p
        CROSS JOIN LATERAL
        (
            SELECT f.edge, f.gridids, ST_LineLocatePoint(f.geom,p.geom) AS fraction, f.start_cost, f.end_cost 
            FROM reached_edges_heatmap f
            WHERE f.geom && ST_Buffer(p.geom,0.0014)
            AND ST_Intersects(f.geom, buffer_edges)
            AND f.partial_edge IS FALSE
            AND f.scenario_id = scenario_edges 
            ORDER BY ST_CLOSESTPOINT(f.geom,p.geom) <-> p.geom
            LIMIT 1      	       	            
        ) AS e
        WHERE p.amenity IN (SELECT UNNEST(select_from_variable_container('pois_one_entrance') || select_from_variable_container('pois_more_entrances')))
        AND ST_Intersects(p.geom,buffer_pois)
        AND (COALESCE(p.scenario_id,0) = 0 OR p.scenario_id = scenario_pois)        
    )
    SELECT p.gid, p.amenity, p.name, p.gridids, interpolate_cost(fraction,start_cost,end_cost)::integer[] AS arr_cost, p.edge, p.fraction, scenario_id_input scenario_id 
    FROM p;

	ALTER TABLE reached_full_edges ADD PRIMARY KEY(gid);

	IF scenario_edges = 0 THEN 	
	  	INSERT INTO reached_pois_heatmap(gid, amenity, name, gridids, arr_cost, edge, fraction, scenario_id)
		SELECT * FROM reached_full_edges;
	END IF;

   	/*Match all POIs that have as closest an partial edge*/
    DROP TABLE IF EXISTS reached_pois_partial; 
   	CREATE TEMP TABLE reached_pois_partial AS 
	SELECT p.gid, p.amenity, p.name, e.gridids, interpolate_cost(p.fraction, e.start_cost, e.end_cost) arr_cost, e.edge, p.fraction, scenario_id_input scenario_id
	FROM reached_full_edges p, reached_edges_heatmap e
	WHERE e.partial_edge IS TRUE
	AND e.scenario_id = scenario_edges
	AND p.edge = e.edge 
	AND p.fraction BETWEEN least(start_perc,end_perc) AND greatest(start_perc,end_perc)
	AND e.geom && buffer_edges;

	CREATE INDEX ON reached_pois_partial (gid);

	IF scenario_edges <> 0  THEN 

		INSERT INTO reached_pois_heatmap(gid, amenity, name, gridids, arr_cost, edge, fraction, scenario_id)
		SELECT f.gid, f.amenity, f.name, c.*, f.edge, f.fraction, scenario_id_input		
		FROM reached_pois_heatmap r, reached_full_edges f, combine_default_scenario_grids(r.gridids, f.gridids, r.arr_cost, f.arr_cost) c
		WHERE r.gid = f.gid
		AND r.scenario_id = 0; 
			
		INSERT INTO reached_pois_heatmap(gid, amenity, name, gridids, arr_cost, edge, fraction, scenario_id)
		SELECT f.*
		FROM reached_full_edges f
		LEFT JOIN reached_pois_heatmap r   
		ON f.gid = r.gid
		WHERE r.gid IS NULL
		AND r.scenario_id = 0; 
		
	END IF; 

    CREATE INDEX ON reached_pois_partial(gid);
   	WITH pois_to_update AS 
	(
		SELECT p.gid, r.gridids, r.gridids # p.gridids[1] arr_position, p.gridids[1] p_gridid, 
		r.arr_cost, p.arr_cost[1] new_cost
		FROM reached_pois_heatmap r, reached_pois_partial p 
		WHERE r.gid = p.gid 
		AND r.gridids && p.gridids
		AND r.arr_cost[r.gridids # p.gridids[1]] > p.arr_cost[1]
		AND r.scenario_id = p.scenario_id
	),
	updated_arrays AS 
	(
		SELECT x.gid, gridids[1:(-1+arr_position)] + p_gridid || gridids[arr_position+1:]  AS gridids, 
		arr_cost[1:(-1+arr_position)] + new_cost || arr_cost[arr_position+1:] AS arr_cost, scenario_id_input scenario_id
		FROM pois_to_update x
	)
	UPDATE reached_pois_heatmap r
	SET gridids = u.gridids, arr_cost = u.arr_cost
	FROM updated_arrays u 
	WHERE r.gid = u.gid
	AND r.scenario_id = u.scenario_id;
	
	DROP TABLE IF EXISTS merged;
	CREATE TEMP TABLE merged AS 
	WITH grids_to_add AS 
	(
		SELECT p.gid, p.amenity, p.name, p.gridids[1] gridids, p.arr_cost[1] arr_cost, p.scenario_id 
		FROM reached_pois_heatmap r, reached_pois_partial p  
		WHERE r.gid = p.gid 
		AND (r.gridids && p.gridids) IS FALSE
		AND r.scenario_id = p.scenario_id
		ORDER BY gid, gridids 
	),
	group_cost_ids AS 
	(
		SELECT gid, scenario_id, array_agg(gridids) gridids, array_agg(arr_cost) arr_cost
		FROM grids_to_add 
		GROUP BY gid, scenario_id 
	)
	SELECT g.gid, g.gridids, g.arr_cost, g.scenario_id 
	FROM group_cost_ids g, reached_full_edges r
	WHERE r.gid = g.gid;

	ALTER TABLE merged ADD PRIMARY key(gid);	

	UPDATE reached_pois_heatmap r
	SET gridids = r.gridids || u.gridids::integer[], arr_cost = r.arr_cost || u.arr_cost::integer[]
	FROM merged u 
	WHERE r.gid = u.gid
	AND r.scenario_id = u.scenario_id;

	INSERT INTO reached_pois_heatmap(gid,amenity,name,gridids,arr_cost,edge,fraction,scenario_id)
	SELECT p.* 
	FROM reached_pois_partial p
	LEFT JOIN (SELECT gid FROM reached_pois_heatmap WHERE scenario_id = scenario_id_input) r
	ON p.gid = r.gid
	WHERE r.gid IS NULL;

	IF scenario_id_input <> 0 THEN
		PERFORM compute_accessibility(scenario_id_input);
	END IF;

END;
$function$ LANGUAGE plpgsql

/*
SELECT reached_pois_heatmap(geom, 0.0014) 
FROM compute_sections 
WHERE section_id = 73
*/