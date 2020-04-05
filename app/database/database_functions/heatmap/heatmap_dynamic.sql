DROP FUNCTION IF EXISTS heatmap_dynamic;
CREATE OR REPLACE FUNCTION public.heatmap_dynamic(userid_input integer, amenities_json jsonb, modus integer)
 RETURNS TABLE(grid_id integer, accessibility_index numeric)
 LANGUAGE plpgsql
AS $function$
DECLARE

	array_amenities text[];
	pois_one_entrance text[] := select_from_variable_container('pois_one_entrance');
	pois_more_entrances text[] := select_from_variable_container('pois_more_entrances');
	excluded_pois_id integer[];
BEGIN
  	
	SELECT array_agg(_keys)
	INTO array_amenities
	FROM (SELECT jsonb_object_keys(amenities_json) _keys)x;


	IF modus = 1 THEN 

		RETURN query 
		SELECT x.grid_id, sum(x.sum)
		FROM (
			SELECT r.grid_id,SUM(EXP(-(cost^2/(amenities_json -> r.amenity ->> 'sensitivity')::integer))*(amenities_json -> r.amenity ->> 'weight')::integer)::NUMERIC  
			FROM reached_pois_heatmap r
			WHERE amenity = ANY(array_amenities)
			AND amenity = ANY(pois_one_entrance)
			GROUP BY r.grid_id
			UNION ALL
			SELECT r.grid_id,SUM(EXP(-(cost^2/(amenities_json -> r.amenity ->> 'sensitivity')::integer))*(amenities_json -> r.amenity ->> 'weight')::integer)::NUMERIC  
			FROM 
			(
				SELECT p.grid_id, min(p.cost) AS cost, p.amenity 
				FROM reached_pois_heatmap p  
				WHERE p.amenity = ANY(array_amenities)
				AND p.amenity = ANY(pois_more_entrances)
				GROUP BY p.grid_id, p.amenity, p.name
			) r
			GROUP BY r.grid_id
		) x
		GROUP BY x.grid_id;
	ELSE 
		DROP TABLE IF EXISTS grid_ids;
		CREATE TEMP TABLE grid_ids AS
		SELECT cells_influenced_by_geom(userid_input,0.01126126) AS grid_id;
		ALTER TABLE grid_ids ADD PRIMARY key(grid_id);
		
		excluded_pois_id = ids_modified_features(userid_input,'pois');
		
		RETURN query 
		WITH computed_grids AS 
		(
			SELECT x.grid_id, sum(x.sum) AS cost
			FROM (
				SELECT r.grid_id, SUM(EXP(-(cost^2/(amenities_json -> r.amenity ->> 'sensitivity')::integer))*(amenities_json -> r.amenity ->> 'weight')::integer)::NUMERIC  
				FROM reached_pois_heatmap r, grid_ids g
				WHERE amenity = ANY(array_amenities)
				AND amenity = ANY(pois_one_entrance)
				AND r.grid_id = g.grid_id
				AND (r.userid = userid_input OR userid IS NULL)
				AND r.poi_gid NOT IN(SELECT UNNEST(excluded_pois_id))
				GROUP BY r.grid_id
				UNION ALL
				SELECT r.grid_id,SUM(EXP(-(cost^2/(amenities_json -> r.amenity ->> 'sensitivity')::integer))*(amenities_json -> r.amenity ->> 'weight')::integer)::NUMERIC  
				FROM 
				(
					SELECT p.grid_id, min(p.cost) AS cost, p.amenity 
					FROM reached_pois_heatmap p, grid_ids g  
					WHERE p.amenity = ANY(array_amenities)
					AND p.amenity = ANY(pois_more_entrances)
					AND p.grid_id = g.grid_id
					AND (p.userid = userid_input OR userid IS NULL)
					AND p.poi_gid NOT IN(SELECT UNNEST(excluded_pois_id))
					GROUP BY p.grid_id, p.amenity, p.name
				) r
				GROUP BY r.grid_id
			) x
			GROUP BY x.grid_id
		),
		grids_now_zero AS (
			SELECT i.grid_id, COALESCE(c.cost,0)
			FROM grid_ids i
			LEFT JOIN computed_grids c
			ON i.grid_id = c.grid_id
			WHERE c.grid_id IS NULL  
		)
		SELECT * FROM computed_grids
		UNION ALL 
		SELECT * FROM grids_now_zero;
	END IF;
END;
$function$;


/*
SELECT * 
FROM heatmap_dynamic(7833128, '{"kindergarten":{"sensitivity":250000,"weight":1},"bus_stop":{"sensitivity":250000,"weight":1}}'::jsonb,1)
*/