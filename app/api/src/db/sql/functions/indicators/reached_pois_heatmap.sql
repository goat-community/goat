CREATE OR REPLACE FUNCTION basic.reached_pois_heatmap(table_name TEXT, calculation_geom geometry, user_id_input integer, scenario_id_input integer DEFAULT 0, data_upload_ids integer[] DEFAULT '{}'::integer[], poi_modified_uid text DEFAULT '')
RETURNS VOID
AS $function$
DECLARE
	sensitivities jsonb:= basic.select_customization('heatmap_sensitivities'); 
	snap_distance integer := basic.select_customization('snap_distance_poi_heatmap')::integer; 
	buffer_pois geometry := ST_BUFFER(calculation_geom::geography, snap_distance)::geometry;
	poi_categories jsonb := basic.poi_categories(user_id_input); 
	arr_categories text[];
BEGIN 
	
	IF table_name = 'poi_user' THEN 
		DELETE FROM customer.reached_poi_heatmap 
		WHERE data_upload_id IN (SELECT UNNEST(data_upload_ids));
	
	ELSEIF table_name = 'poi_modified' THEN 
		DELETE FROM customer.reached_poi_heatmap r
		WHERE poi_uid = poi_modified_uid
		AND scenario_id = scenario_id_input;
	
	END IF; 

	WITH categories AS
	(
		SELECT jsonb_array_elements_text(basic.poi_categories(user_id_input) -> 'true') AS category
		UNION ALL 
		SELECT jsonb_array_elements_text(basic.poi_categories(user_id_input) -> 'false') AS category
	)
	SELECT array_agg(category)
	FROM categories 
	INTO arr_categories; 
	
	IF table_name = 'poi' THEN 
		DROP TABLE IF EXISTS pois_edges_full;
		CREATE TEMP TABLE pois_edges_full AS 
		SELECT p.uid AS poi_uid, f.fraction, f.edge_id, NULL AS scenario_id, NULL AS data_upload_id  
		FROM (
			SELECT p.* 
			FROM basic.poi p
			LEFT JOIN customer.reached_poi_heatmap r 
			ON r.poi_uid = p.uid
			WHERE r.poi_uid IS NULL
		) p  
		CROSS JOIN LATERAL 
		(
			SELECT ST_LineLocatePoint(e.geom,p.geom) fraction, e.edge_id
			FROM customer.reached_edge_full_heatmap e 
			WHERE e.geom && ST_Buffer(p.geom::geography, snap_distance)::geometry
			ORDER BY ST_CLOSESTPOINT(e.geom, p.geom) <-> p.geom 
			LIMIT 1 
		) AS f
		WHERE p.category IN (SELECT UNNEST(arr_categories))
		AND ST_Intersects(p.geom, buffer_pois); 
	ELSEIF table_name = 'poi_user' THEN 
		DROP TABLE IF EXISTS pois_edges_full;
		CREATE TEMP TABLE pois_edges_full AS 
		SELECT p.uid AS poi_uid, f.fraction, f.edge_id, NULL AS scenario_id, p.data_upload_id 
		FROM 
		(
			SELECT p.* 
			FROM customer.poi_user p
			LEFT JOIN customer.reached_poi_heatmap r 
			ON r.poi_uid = p.uid
			WHERE r.poi_uid IS NULL
		) p 
		CROSS JOIN LATERAL 
		(
			SELECT ST_LineLocatePoint(e.geom,p.geom) fraction, e.edge_id
			FROM customer.reached_edge_full_heatmap e 
			WHERE e.geom && ST_Buffer(p.geom::geography, snap_distance)::geometry
			ORDER BY ST_CLOSESTPOINT(e.geom, p.geom) <-> p.geom 
			LIMIT 1 
		) AS f
		WHERE ST_Intersects(p.geom, buffer_pois)
		AND p.data_upload_id IN (SELECT UNNEST(data_upload_ids)); 
	ELSEIF table_name = 'poi_modified' THEN 
		DROP TABLE IF EXISTS pois_edges_full;
		CREATE TEMP TABLE pois_edges_full AS 
		SELECT p.uid AS poi_uid, f.fraction, f.edge_id, scenario_id_input AS scenario_id, p.data_upload_id  
		FROM (
			SELECT p.* 
			FROM customer.poi_modified p 
			WHERE p.uid = poi_modified_uid 
			AND p.scenario_id = scenario_id_input
		) p
		CROSS JOIN LATERAL 
		(
			SELECT ST_LineLocatePoint(e.geom,p.geom) fraction, e.edge_id
			FROM customer.reached_edge_full_heatmap e 
			WHERE e.geom && ST_Buffer(p.geom::geography, snap_distance)::geometry
			ORDER BY ST_CLOSESTPOINT(e.geom, p.geom) <-> p.geom 
			LIMIT 1 
		) AS f;
	ELSE 
		RAISE EXCEPTION 'Please specify a valid table name.';
	END IF;
	
	CREATE INDEX ON pois_edges_full (edge_id);	
	INSERT INTO customer.reached_poi_heatmap(poi_uid, scenario_id, data_upload_id, grid_visualization_ids, costs, accessibility_indices)
	WITH pois_with_cost AS 
	(
		SELECT f.poi_uid, f.scenario_id, c.grid_visualization_id, c.COST, f.data_upload_id 
		FROM pois_edges_full f
		CROSS JOIN LATERAL 
		(
			SELECT e.grid_visualization_id, avg(e.cost) AS COST 
			FROM 
			(
				SELECT c.grid_visualization_id,
				CASE WHEN r.start_cost < r.end_cost THEN (r.start_cost + f.fraction * (r.end_cost-r.start_cost))
				ELSE (r.end_cost + (1-f.fraction) * (r.start_cost - r.end_cost)) END AS COST
				FROM customer.reached_edge_heatmap_grid_calculation r, basic.grid_calculation c 
				WHERE f.edge_id = r.reached_edge_heatmap_id 
				AND (r.edge_type IS NULL or r.edge_type = 'a')
				AND r.grid_calculation_id = c.id
				UNION ALL 
				SELECT c.grid_visualization_id, CASE WHEN start_cost < end_cost THEN (start_cost + fraction * (end_cost-start_cost))
				ELSE (end_cost + (1-fraction) * (start_cost - end_cost)) END AS COST
				FROM customer.reached_edge_heatmap_grid_calculation r, basic.grid_calculation c 
				WHERE f.edge_id = r.reached_edge_heatmap_id 
				AND edge_type IN ('p', 'ap')
				AND f.fraction BETWEEN least(r.start_perc,r.end_perc) AND greatest(r.start_perc,r.end_perc)		
				AND r.grid_calculation_id = c.id
			) e	
			GROUP BY e.grid_visualization_id 
		) AS c 
	),
	first_merge AS
	(
		SELECT poi_uid, scenario_id, data_upload_id, array_agg(grid_visualization_id) AS grid_visualization_ids , array_agg(cost) AS costs   
		FROM pois_with_cost 
		GROUP BY poi_uid, scenario_id, data_upload_id  
	)
	SELECT f.poi_uid, f.scenario_id::integer, f.data_upload_id::integer, f.grid_visualization_ids, f.costs, a.accessibility_indices
	FROM first_merge f
	CROSS JOIN LATERAL 
	(
		SELECT ARRAY_AGG(accessibility_indices) AS accessibility_indices 
		FROM 
		(
			SELECT array_AGG((pow(exp(1.0)::real,(p.cost::real * p.cost::real) / -s.sensitivity) * (10000))::integer) AS accessibility_indices, s.sensitivity  
			FROM (SELECT sensitivity::REAL FROM jsonb_array_elements(basic.select_customization('heatmap_sensitivities')) sensitivity) s, 
			(SELECT UNNEST(f.costs) cost) p
			GROUP BY sensitivity 
			ORDER BY sensitivity 
		) s
	) AS a;
	
END;
$function$ LANGUAGE plpgsql

/*
EXPLAIN ANALYZE 
SELECT basic.reached_pois_heatmap('poi_modified'::text, geom, 4, 75, ARRAY[0]::integer[], 'd0c79777fcdc4d55b02da0ef17470bef'::text) 
FROM (SELECT * FROM customer.poi_modified pm WHERE uid = 'd0c79777fcdc4d55b02da0ef17470bef') p
*/
