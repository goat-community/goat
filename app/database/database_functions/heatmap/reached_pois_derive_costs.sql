
DROP FUNCTION IF EXISTS reached_pois_derive_costs;
CREATE OR REPLACE FUNCTION public.reached_pois_derive_costs(buffer_geom geometry, sensitivities integer[], snap_distance NUMERIC, userid_input integer DEFAULT 0, scenario_id_input integer DEFAULT 0)
RETURNS VOID
AS $function$

BEGIN 
		INSERT INTO reached_pois_heatmap(gid,amenity,name,gridids,arr_cost,accessibility_indices, userid, scenario_id)
		WITH p AS 
        (
            SELECT p.gid, p.amenity, p.name, p.geom, e.edge, e.gridids, e.fraction, e.start_cost, e.end_cost
            FROM pois_userinput p
            CROSS JOIN LATERAL
            (
                SELECT f.edge, f.gridids, ST_LineLocatePoint(f.geom,p.geom) AS fraction, f.start_cost, f.end_cost 
                FROM reached_edges_heatmap f
                WHERE f.geom && ST_Buffer(p.geom,snap_distance)
                AND ST_Intersects(f.geom,ST_BUFFER(buffer_geom,snap_distance))
                AND f.partial_edge IS FALSE
                AND f.userid = userid_input
                AND f.scenario_id = scenario_id_input
                ORDER BY ST_CLOSESTPOINT(f.geom,p.geom) <-> p.geom
                LIMIT 1
            ) AS e
            WHERE p.amenity IN (SELECT UNNEST(select_from_variable_container('pois_one_entrance') || select_from_variable_container('pois_more_entrances')))
            AND ST_Intersects(p.geom,buffer_geom)
            AND (p.userid IS NULL OR (p.userid = userid_input AND p.scenario_id = scenario_id_input))
        )
        SELECT p.gid, p.amenity, p.name, p.gridids, c.arr_true_cost arr_cost, c.accessibility_indices::integer[],userid_input userid, scenario_id_input scenario_id 
        FROM p, compute_accessibility_index(fraction,start_cost,end_cost,sensitivities) c;
      
	   	DROP TABLE IF EXISTS reached_pois_partial;
       	CREATE TABLE reached_pois_partial AS 
	   	WITH p AS 
	    (
	        SELECT p.gid, p.amenity, p.name, p.geom, e.edge, e.gridids, e.fraction, e.start_cost, e.end_cost
	        FROM pois_userinput p
	        CROSS JOIN LATERAL
	        (
	            SELECT f.edge, f.gridids, ST_LineLocatePoint(f.geom,p.geom) AS fraction, f.start_cost, f.end_cost 
	            FROM reached_edges_heatmap f
	            WHERE f.geom && ST_Buffer(p.geom,snap_distance)
	            AND ST_Intersects(f.geom,ST_BUFFER(buffer_geom,snap_distance))
	            AND partial_edge IS TRUE
	            AND f.userid = userid_input
                AND f.scenario_id = scenario_id_input
	            ORDER BY ST_CLOSESTPOINT(f.geom,p.geom) <-> p.geom
	            LIMIT 1
	        ) AS e
	        WHERE p.amenity IN (SELECT UNNEST(select_from_variable_container('pois_one_entrance') || select_from_variable_container('pois_more_entrances')))
	        AND ST_Intersects(p.geom,buffer_geom)
	        AND (p.userid IS NULL OR (p.userid = userid_input AND p.scenario_id = scenario_id_input))
	    )
	    SELECT p.gid, p.amenity, p.name, p.gridids, c.arr_true_cost arr_cost, c.accessibility_indices::integer[],userid_input userid, scenario_id_input scenario_id 
	    FROM p, compute_accessibility_index(fraction,start_cost,end_cost,sensitivities) c;
	   	
	   	CREATE INDEX ON reached_pois_partial(gid);
	   
	   	WITH pois_to_update AS 
		(
			SELECT p.gid, r.gridids, r.gridids # p.gridids[1] arr_position, 
			r.gridids - p.gridids[1] + p.gridids[1] new_gridids, p.gridids[1], r.arr_cost, p.arr_cost[1] new_cost, r.accessibility_indices a1, p.accessibility_indices a2
			FROM reached_pois_heatmap r, reached_pois_partial p 
			WHERE r.gid = p.gid 
			AND r.gridids && p.gridids
			AND r.arr_cost[r.gridids # p.gridids[1]] > p.arr_cost[1]
			AND r.userid = p.userid
			AND r.scenario_id = p.scenario_id
		),
		updated_arrays AS 
		(
			SELECT x.gid, new_gridids AS gridids, arr_cost[1:(-1+arr_position)] + new_cost || arr_cost[arr_position+1:] AS arr_cost, 
			update_accessibility_array(x.a1, x.a2, arr_position) AS accessibility_indices, userid_input userid, scenario_id_input scenario_id
			FROM pois_to_update x
		)
		UPDATE reached_pois_heatmap r
		SET gridids = u.gridids, arr_cost = u.arr_cost, accessibility_indices = u.accessibility_indices
		FROM updated_arrays u 
		WHERE r.gid = u.gid
		AND r.userid = u.userid
		AND r.scenario_id = u.scenario_id;
       	
		WITH grids_to_add AS 
		(
			SELECT p.gid, r.gridids + p.gridids[1] gridids, r.arr_cost + p.arr_cost[1] arr_cost,
			append_accessibility_array(r.accessibility_indices, p.accessibility_indices) AS accessibility_indices, p.userid, p.scenario_id 
			FROM reached_pois_heatmap r, reached_pois_partial p  
			WHERE r.gid = p.gid 
			AND (r.gridids && p.gridids) IS FALSE
			AND r.userid = p.userid
			AND r.scenario_id = p.scenario_id
		)
		UPDATE reached_pois_heatmap r
		SET gridids = u.gridids, arr_cost = u.arr_cost, accessibility_indices = u.accessibility_indices
		FROM grids_to_add u 
		WHERE r.gid = u.gid
		AND r.userid = u.userid
		AND r.scenario_id = u.scenario_id;
				
		INSERT INTO reached_pois_heatmap(gid,amenity,name,gridids,arr_cost,accessibility_indices,userid,scenario_id)
		SELECT p.* 
		FROM reached_pois_partial p
		LEFT JOIN (SELECT gid FROM reached_pois_heatmap WHERE userid = userid_input AND scenario_id = scenario_id_input) r
		ON p.gid = r.gid
		WHERE r.gid IS NULL;

END;
$function$ LANGUAGE plpgsql