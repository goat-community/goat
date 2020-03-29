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
		GROUP BY r.grid_id;
	ELSE 
		DROP TABLE IF EXISTS grid_ids;
		CREATE TEMP TABLE grid_ids AS
		SELECT cells_influenced_by_geom(userid_input,0.01126126) AS grid_id;
		ALTER TABLE grid_ids ADD PRIMARY key(grid_id);
		
		excluded_pois_id = ids_modified_features(userid_input,'pois');
		
		RETURN query 
		SELECT r.grid_id,SUM(EXP(-(cost^2/(amenities_json -> r.amenity ->> 'sensitivity')::integer))*(amenities_json -> r.amenity ->> 'weight')::integer)::NUMERIC  
		FROM reached_pois_heatmap r, grid_ids g
		WHERE amenity = ANY(array_amenities)
		AND amenity = ANY(pois_one_entrance)
		AND r.grid_id = g.grid_id
		AND (r.userid = userid_input OR userid IS NULL)
		AND r.poi_gid != ANY(excluded_pois_id)
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
			AND p.poi_gid != ANY(excluded_pois_id)
			GROUP BY p.grid_id, p.amenity, p.name
		) r
		GROUP BY r.grid_id;
	END IF;
	--One entrance and two entrances separate!	*/
END;
$function$;




EXPLAIN ANALYZE
SELECT * 
FROM heatmap2(7833128, '{"kindergarten":{"sensitivity":2500000,"weight":1},"bus_stop":{"sensitivity":2500000,"weight":1}}'::jsonb,1)


/*
SELECT * FROM heatmap2(1,'{"kindergarten":{"sensitivity":-0.003,"weight":1},"primary_school":{"sensitivity":-0.003,"weight":1},"secondary_school":{"sensitivity":-0.003,"weight":1},"library":{"sensitivity":-0.003,"weight":1},
"bar":{"sensitivity":-0.003,"weight":1},"biergarten":{"sensitivity":-0.003,"weight":1},"cafe":{"sensitivity":-0.003,"weight":1},"pub":{"sensitivity":-0.003,"weight":1},"fast_food":{"sensitivity":-0.003,"weight":1},
"ice_cream":{"sensitivity":-0.003,"weight":1},"restaurant":{"sensitivity":-0.003,"weight":1},"nightclub":{"sensitivity":-0.003,"weight":1},
"bicycle_rental":{"sensitivity":-0.003,"weight":1},"car_sharing":{"sensitivity":-0.003,"weight":1},
"charging_station":{"sensitivity":-0.003,"weight":1},"bus_stop":{"sensitivity":-0.003,"weight":1}}'::jsonb)
*/