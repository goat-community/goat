DROP FUNCTION IF EXISTS reached_population_pois;
CREATE OR REPLACE FUNCTION public.reached_population_pois(buffer_geom geometry, snap_distance NUMERIC, combination_scenarios text DEFAULT 'default', scenario_id_input integer DEFAULT 0)
RETURNS VOID
AS $function$
DECLARE
	sensitivities integer[] := select_from_variable_container('heatmap_sensitivities');
	series_sensitivities integer[]; 
	scenario_edges integer := 0;
	scenario_pois integer := 0;
	cnt_scenario_edges integer; 
	buffer_edges geometry; 
	buffer_pop geometry;
BEGIN 
	
	SELECT count(*) 
	INTO cnt_scenario_edges
	FROM 
	(
		SELECT *
		FROM reached_edges_pois 
		WHERE scenario_id = scenario_id_input 
		AND ST_Intersects(geom, buffer_geom) LIMIT 1
	) x;
	
	buffer_edges = ST_BUFFER(buffer_geom,0.0014);
	buffer_pop = buffer_geom;
	
	/*This is preliminary. We need a better way for handling the scenarios. */
	IF combination_scenarios = 'default' THEN /*No Scenario*/
		scenario_edges = 0;
		scenario_pois = 0;
		RAISE NOTICE '%',scenario_edges;
	ELSEIF combination_scenarios = 'scenario' /*POIs and edges scenario*/ AND cnt_scenario_edges > 0 THEN 
		scenario_edges = scenario_id_input;
		scenario_pois = scenario_id_input;
		buffer_pop = buffer_edges;
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
/*Problem:pois are stored as an array; but i want every poi to be in a single column for the reached_population_pois*/

	CREATE /*TEMP*/ TABLE reached_full_edges AS 
	WITH p AS 
    (
        SELECT p.gid as pop_gid, p.population, p.geom, e.edge, e.amenity, e.gids, e.fraction, e.start_cost, e.end_cost, e.scenario_id
        FROM population p
        CROSS JOIN LATERAL
        (
            SELECT f.edge, f.gids, f.amenity, ST_LineLocatePoint(f.geom,p.geom) AS fraction, f.start_cost, f.end_cost, f.scenario_id
            FROM reached_edges_pois f
            WHERE f.geom && ST_Buffer(p.geom,0.0014)
            AND ST_Intersects(f.geom, buffer_edges)
            AND f.partial_edge IS FALSE 
            AND f.scenario_id = scenario_edges 
            ORDER BY ST_CLOSESTPOINT(f.geom,p.geom) <-> p.geom
            LIMIT 1      	       	            
        ) AS e
        WHERE ST_Intersects(p.geom,buffer_pop)
        AND (COALESCE(e.scenario_id,0) = 0 OR e.scenario_id = scenario_pois)        
    )
    SELECT p.pop_gid, p.population, p.amenity, p.gids, interpolate_cost(p.fraction,p.start_cost,p.end_cost)::integer[] AS arr_cost, p.edge, p.fraction, scenario_id_input scenario_id 
    FROM p;

	ALTER TABLE reached_full_edges ADD PRIMARY KEY(pop_gid);

	IF scenario_edges = 0 THEN 	
	  	INSERT INTO reached_population_pois (pop_gid, population, amenity, gids, arr_cost, edge, fraction, scenario_id)
		SELECT * FROM reached_full_edges;
	END IF;

   	/*Match all POIs that have as closest an partial edge*/
    DROP TABLE IF EXISTS reached_pop_partial; 
   	CREATE /*TEMP*/ TABLE reached_pop_partial AS 
	SELECT p.pop_gid, p.population, e.amenity, e.gids, interpolate_cost(p.fraction, e.start_cost, e.end_cost) arr_cost, e.edge, p.fraction, scenario_id_input scenario_id
	FROM reached_full_edges p, reached_edges_pois e
	WHERE e.partial_edge IS TRUE
	AND e.scenario_id = scenario_edges
	AND p.edge = e.edge 
	AND p.fraction BETWEEN least(start_perc,end_perc) AND greatest(start_perc,end_perc)
	AND e.geom && buffer_edges;

	CREATE INDEX ON reached_pop_partial (pop_gid);

	IF scenario_edges <> 0  THEN 

		INSERT INTO reached_population_pois(pop_gid, population, amenity, gids, arr_cost, edge, fraction, scenario_id)
		SELECT f.pop_gid, f.population, f.amenity, f.gids, c.*, f.edge, f.fraction, scenario_id_input		
		FROM reached_population_pois r, reached_full_edges f, combine_default_scenario_grids(r.gids, f.gids, r.arr_cost, f.arr_cost) c
		WHERE r.pop_gid = f.pop_gid
		AND r.scenario_id = 0; 
			
		INSERT INTO reached_population_pois(pop_gid, population, amenity, gids, arr_cost, edge, fraction, scenario_id)
		SELECT f.*
		FROM reached_full_edges f
		LEFT JOIN reached_population_pois r   
		ON f.pop_gid = r.pop_gid
		WHERE r.pop_gid IS NULL
		AND r.scenario_id = 0; 
		
	END IF; 

    CREATE INDEX ON reached_pop_partial(pop_gid);
   	WITH pois_to_update AS 
	(
		SELECT p.pop_gid, r.population, r.amenity, r.gids, r.gids # p.gids[1] arr_position, p.gids[1] p_gids, 
		r.arr_cost, p.arr_cost[1] new_cost
		FROM reached_population_pois r, reached_pop_partial p 
		WHERE r.pop_gid = p.pop_gid 
		AND r.gids && p.gids
		AND r.arr_cost[r.gids # p.gids[1]] > p.arr_cost[1]
		AND r.scenario_id = p.scenario_id
	),
	updated_arrays AS 
	(
		SELECT x.pop_gid, gids[1:(-1+arr_position)] + p_gids || gids[arr_position+1:]  AS gids, 
		arr_cost[1:(-1+arr_position)] + new_cost || arr_cost[arr_position+1:] AS arr_cost, scenario_id_input scenario_id
		FROM pois_to_update x
	)
	UPDATE reached_population_pois r
	SET gids = u.gids, arr_cost = u.arr_cost
	FROM updated_arrays u 
	WHERE r.pop_gid = u.pop_gid
	AND r.scenario_id = u.scenario_id;
	
	DROP TABLE IF EXISTS merged;
	CREATE /*TEMP*/ TABLE merged AS 
	WITH gids_to_add AS 
	(
		SELECT p.pop_gid, p.population, r.amenity, p.gids[1] gids, p.arr_cost[1] arr_cost, p.scenario_id 
		FROM reached_population_pois r, reached_pop_partial p  
		WHERE r.pop_gid = p.pop_gid 
		AND (r.gids && p.gids) IS FALSE
		AND r.scenario_id = p.scenario_id
		ORDER BY pop_gid, gids 
	),
	group_cost_ids AS 
	(
		SELECT pop_gid, scenario_id, amenity, array_agg(gids) gids, array_agg(arr_cost) arr_cost
		FROM gids_to_add 
		GROUP BY pop_gid, amenity, scenario_id 
	)
	SELECT g.pop_gid, g.amenity, g.gids, g.arr_cost, g.scenario_id 
	FROM group_cost_ids g, reached_full_edges r
	WHERE r.pop_gid = g.pop_gid;

	ALTER TABLE merged ADD PRIMARY key(pop_gid);	

	UPDATE reached_population_pois r
	SET gids = r.gids || u.gids::integer[], arr_cost = r.arr_cost || u.arr_cost::integer[]
	FROM merged u 
	WHERE r.pop_gid = u.pop_gid
	AND r.scenario_id = u.scenario_id;

	INSERT INTO reached_population_pois(pop_gid,population,amenity,gids,arr_cost,edge,fraction,scenario_id)
	SELECT p.* 
	FROM reached_pop_partial p
	LEFT JOIN (SELECT pop_gid FROM reached_population_pois WHERE scenario_id = scenario_id_input) r
	ON p.pop_gid = r.pop_gid
	WHERE r.pop_gid IS NULL;

	IF scenario_id_input <> 0 THEN
		PERFORM compute_accessibility_pois(scenario_id_input);
	END IF;

END;
$function$ LANGUAGE plpgsql

/*
SELECT reached_pois_heatmap(geom, 0.0014) 
FROM compute_sections 
WHERE section_id = 73
*/