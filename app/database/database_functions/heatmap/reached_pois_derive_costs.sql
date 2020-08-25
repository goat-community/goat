
DROP FUNCTION IF EXISTS reached_pois_derive_costs;
CREATE OR REPLACE FUNCTION public.reached_pois_derive_costs(buffer_geom geometry, sensitivities integer[], snap_distance NUMERIC, userid_input integer DEFAULT 0, scenario_id_input integer DEFAULT 0)
RETURNS VOID
AS $function$
DECLARE
	series_sensitivities integer[]; 
BEGIN 
	series_sensitivities = (SELECT array_agg(x.s)
	FROM (SELECT generate_series(1,ARRAY_LENGTH(ARRAY[1,2,3,4,5,6,7],1)) s) x);

	DROP TABLE IF EXISTS reached_full_edges;
	CREATE TEMP TABLE reached_full_edges AS 
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
    SELECT p.gid, p.amenity, p.name, p.gridids, c.arr_true_cost arr_cost, p.edge, p.fraction, c.accessibility_indices::integer[],userid_input userid, scenario_id_input scenario_id 
    FROM p, compute_accessibility_index(fraction,start_cost,end_cost,sensitivities) c;
	    
   	INSERT INTO reached_pois_heatmap(gid, amenity, name, gridids, arr_cost, edge, fraction, accessibility_indices, userid, scenario_id)
	SELECT * FROM reached_full_edges;

   	/*Inject here*/
   	DROP TABLE IF EXISTS reached_pois_partial; 
   	CREATE TEMP TABLE reached_pois_partial AS 
	SELECT p.gid, p.amenity, p.name, e.gridids, c.arr_true_cost arr_cost, e.edge, p.fraction, c.accessibility_indices::integer[],userid_input userid, scenario_id_input scenario_id
	FROM reached_full_edges p, reached_edges_heatmap e, compute_accessibility_index(p.fraction, e.start_cost, e.end_cost, sensitivities) c
	WHERE e.partial_edge IS TRUE
	AND p.edge = e.edge 
	AND p.fraction BETWEEN least(start_perc,end_perc) AND greatest(start_perc,end_perc)
	AND e.geom && ST_BUFFER(buffer_geom,snap_distance);
	
    CREATE INDEX ON reached_pois_partial(gid);
   	WITH pois_to_update AS 
	(
		SELECT p.gid, r.gridids, r.gridids # p.gridids[1] arr_position, p.gridids[1] p_gridid, 
		r.arr_cost, p.arr_cost[1] new_cost, r.accessibility_indices a1, p.accessibility_indices a2
		FROM reached_pois_heatmap r, reached_pois_partial p 
		WHERE r.gid = p.gid 
		AND r.gridids && p.gridids
		AND r.arr_cost[r.gridids # p.gridids[1]] > p.arr_cost[1]
		AND r.userid = p.userid
		AND r.scenario_id = p.scenario_id
	),
	updated_arrays AS 
	(
		SELECT x.gid, gridids[1:(-1+arr_position)] + p_gridid || gridids[arr_position+1:]  AS gridids, arr_cost[1:(-1+arr_position)] + new_cost || arr_cost[arr_position+1:] AS arr_cost, 
		update_accessibility_array(x.a1, x.a2, arr_position) AS accessibility_indices, userid_input userid, scenario_id_input scenario_id
		FROM pois_to_update x
	)
	UPDATE reached_pois_heatmap r
	SET gridids = u.gridids, arr_cost = u.arr_cost, accessibility_indices = u.accessibility_indices
	FROM updated_arrays u 
	WHERE r.gid = u.gid
	AND r.userid = u.userid
	AND r.scenario_id = u.scenario_id;
	
	DROP TABLE IF EXISTS merged;
	CREATE TEMP TABLE merged AS 
	WITH grids_to_add AS 
	(
		SELECT p.gid, p.amenity, p.name, p.gridids[1] gridids, p.arr_cost[1] arr_cost,
		p.accessibility_indices AS accessibility_indices, p.userid, p.scenario_id 
		FROM reached_pois_heatmap r, reached_pois_partial p  
		WHERE r.gid = p.gid 
		AND (r.gridids && p.gridids) IS FALSE
		AND r.userid = 0
		AND r.scenario_id = 0
		ORDER BY gid, gridids 
	),
	group_cost_ids AS 
	(
		SELECT gid,userid, scenario_id, array_agg(gridids) gridids, array_agg(arr_cost) arr_cost
		FROM grids_to_add 
		GROUP BY gid, userid, scenario_id 
	),		
	unnest_helper AS 
	(
		SELECT gid, gridids, arr_cost,
		UNNEST(accessibility_indices) accessibility_indices , UNNEST(ARRAY[1,2,3,4,5,6,7]) arr_position --UNNEST(series_sensitivities)
		FROM grids_to_add 
	),
	first_nesting AS 
	(
		SELECT gid, array_agg(accessibility_indices) accessibility_indices
		FROM unnest_helper
		GROUP BY gid, arr_position
	),
	second_nesting AS 
	(
		SELECT gid, array_agg(accessibility_indices) accessibility_indices
		FROM first_nesting 
		GROUP BY gid 
	)
	SELECT g.gid, g.gridids, g.arr_cost, s. accessibility_indices, g.userid, g.scenario_id 
	FROM group_cost_ids g, second_nesting s
	WHERE g.gid = s.gid;

	ALTER TABLE merged ADD PRIMARY key(gid);	
	
	SELECT * FROM merged 

	UPDATE reached_pois_heatmap r
	SET gridids = r.gridids || u.gridids::integer[], arr_cost = r.arr_cost || u.arr_cost::integer[], accessibility_indices = r.accessibility_indices || u.accessibility_indices
	FROM merged u 
	WHERE r.gid = u.gid
	AND r.userid = u.userid
	AND r.scenario_id = u.scenario_id;

	INSERT INTO reached_pois_heatmap(gid,amenity,name,gridids,arr_cost,edge,fraction,accessibility_indices,userid,scenario_id)
	SELECT p.* 
	FROM reached_pois_partial p
	LEFT JOIN (SELECT gid FROM reached_pois_heatmap WHERE userid = userid_input AND scenario_id = scenario_id_input) r
	ON p.gid = r.gid
	WHERE r.gid IS NULL;
		
END;
$function$ LANGUAGE plpgsql

SELECT * FROM reached_pois_partial rpp WHERE gridids && ARRAY[3559] AND amenity = 'restaurant' ORDER BY name 

SELECT * FROM reached_pois_heatmap rpp WHERE  amenity = 'restaurant' ORDER BY name 

SELECT * FROM reached_full_edges rpp WHERE gridids && ARRAY[3559]

SELECT * FROM reached_edges_heatmap reh WHERE edge = 96121

   SELECT p.gid, p.amenity, p.name, p.gridids, c.arr_true_cost arr_cost, p.edge, p.fraction, c.accessibility_indices::integer[],userid_input userid, scenario_id_input scenario_id 
        FROM p, compute_accessibility_index(fraction,start_cost,end_cost,sensitivities) c;
   		

DROP TABLE test_edges; 

CREATE TABLE test_edges AS 
SELECT geom, start_cost[gridids # 3559], end_cost[gridids # 3559] FROM reached_edges_heatmap reh WHERE gridids && ARRAY[3559]

DROP TABLE test_pois;
CREATE TABLE test_pois AS 
SELECT r.*,arr_cost[gridids # 3559] AS COST, p.geom 
FROM reached_pois_heatmap r, pois p 
WHERE gridids && ARRAY[3559]
AND r.gid = p.gid;

SELECT * FROM reached_edges_heatmap WHERE partial_edge IS TRUE 


buffer_geom geometry, sensitivities integer[], snap_distance NUMERIC, userid_input integer DEFAULT 0, scenario_id_input integer DEFAULT 0)

SELECT * FROM variable_container vc 


DELETE FROM reached_pois_heatmap 

SELECT reached_pois_derive_costs(geom,ARRAY[150000,200000,250000,300000,350000,400000,450000],0.0014) 
FROM compute_sections 
WHERE section_id = 73

SELECT * FROM reached_pois_partial rpp 


DROP TABLE test_pois; 
CREATE TABLE test_pois AS

ALTER TABLE reached_full_edges ADD COLUMN id serial;
ALTER TABLE reached_full_edges ADD PRIMARY key(id);
CREATE INDEX ON reached_full_edges (edge);

CREATE INDEX ON reached_edges_heatmap (partial_edge)

CREATE TABLE test_partial AS 

EXPLAIN ANALYZE 
SELECT * FROM reached_edges_heatmap 
WHERE geom && (
SELECT geom
FROM compute_sections cs 
WHERE section_id = 73
)


EXPLAIN ANALYZE 

DROP TABLE reached_pois_partial;



SELECT * FROM reached_pois_partial rpp 

SELECT * FROM reached_edges_heatmap 


SELECT * FROM pois WHERE name = 'Oberlandmetzger'

SELECT count(*) FROM reached_pois_partial 

SELECT count(*) FROM reached_pois_heatmap 

CREATE TABLE test_partial_pois AS 
SELECT * FROM reached_pois_partial, pois p 
WHERE r.gid = p.gid






