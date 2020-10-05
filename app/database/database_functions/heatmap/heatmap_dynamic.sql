DROP FUNCTION IF EXISTS heatmap_dynamic;
CREATE OR REPLACE FUNCTION public.heatmap_dynamic(amenities_json jsonb, modus_input text DEFAULT 'default', scenario_id_input integer DEFAULT 0)
 RETURNS TABLE(grid_id integer, accessibility_index bigint)
 LANGUAGE plpgsql
AS $function$
DECLARE
	array_amenities text[];
	pois_one_entrance text[] := select_from_variable_container('pois_one_entrance');
	pois_more_entrances text[] := select_from_variable_container('pois_more_entrances');
	sensitivities integer[] := select_from_variable_container('heatmap_sensitivities')::integer[];
	translation_sensitivities jsonb;
	excluded_pois_id integer[];
BEGIN
  	
	SELECT array_agg(_keys)
	INTO array_amenities
	FROM (SELECT jsonb_object_keys(amenities_json) _keys) x;
	
	SELECT jsonb_object_agg(k, (sensitivities  # (v ->> 'sensitivity')::integer)::smallint)
	INTO translation_sensitivities
	FROM jsonb_each(amenities_json) AS u(k, v);

	IF modus_input = 'default' THEN 
		RETURN query 
		SELECT s.grid_id, sum(s.accessibility_index) AS accessibility_index 
		FROM 
		(
			SELECT u.grid_id, u.accessibility_index * (amenities_json -> x.amenity ->> 'weight')::SMALLINT AS accessibility_index  
			FROM (
				SELECT gridids, amenity, accessibility_indices[(translation_sensitivities ->> amenity)::integer:(translation_sensitivities ->> amenity)::integer][1:]
				FROM reached_pois_heatmap 
				WHERE amenity IN (SELECT UNNEST(pois_one_entrance))
				AND amenity IN (SELECT UNNEST(array_amenities))
				AND scenario_id = 0
			)x, UNNEST(x.gridids, x.accessibility_indices) AS u(grid_id, accessibility_index)
			UNION ALL 
			SELECT u.grid_id, max(u.accessibility_index) * (amenities_json -> x.amenity ->> 'weight')::SMALLINT AS accessibility_index
			FROM (
				SELECT gridids, amenity, name,  accessibility_indices[(translation_sensitivities ->> amenity)::integer:(translation_sensitivities ->> amenity)::integer][1:]
				FROM reached_pois_heatmap
				WHERE amenity IN (SELECT UNNEST(pois_more_entrances))
				AND amenity IN (SELECT UNNEST(array_amenities))
				AND scenario_id = 0
			)x, UNNEST(x.gridids, x.accessibility_indices) AS u(grid_id, accessibility_index)
			GROUP BY u.grid_id, x.amenity, x.name
		) s
		GROUP BY s.grid_id;
	ELSE
		excluded_pois_id = ids_modified_features(scenario_id_input,'pois');
		RETURN query 
		WITH null_grids AS 
		(
			SELECT DISTINCT UNNEST(gridids) grid_id,0 accessibility_index
			FROM reached_pois_heatmap 
			WHERE gid IN (SELECT UNNEST(excluded_pois_id))
		),
		grouped_grids AS 
		(
			SELECT s.grid_id, sum(s.accessibility_index) AS accessibility_index 
			FROM 
			(
				SELECT u.grid_id, u.accessibility_index * (amenities_json -> x.amenity ->> 'weight')::SMALLINT AS accessibility_index  
				FROM (
					SELECT gridids, amenity, accessibility_indices[(translation_sensitivities ->> amenity)::integer:(translation_sensitivities ->> amenity)::integer][1:]
					FROM reached_pois_heatmap 
					WHERE amenity IN (SELECT UNNEST(pois_one_entrance))
					AND amenity IN (SELECT UNNEST(array_amenities))
					AND scenario_id IN(scenario_id_input,0)
					AND gid NOT IN (SELECT UNNEST(excluded_pois_id))
				)x, UNNEST(x.gridids, x.accessibility_indices) AS u(grid_id, accessibility_index)
				UNION ALL 
				SELECT u.grid_id, max(u.accessibility_index) * (amenities_json -> x.amenity ->> 'weight')::SMALLINT AS accessibility_index
				FROM (
					SELECT gridids, amenity, name,  accessibility_indices[(translation_sensitivities ->> amenity)::integer:(translation_sensitivities ->> amenity)::integer][1:]
					FROM reached_pois_heatmap
					WHERE amenity IN (SELECT UNNEST(pois_more_entrances))
					AND amenity IN (SELECT UNNEST(array_amenities))
					AND scenario_id IN(scenario_id_input,0)
					AND gid NOT IN (SELECT UNNEST(excluded_pois_id))
				)x, UNNEST(x.gridids, x.accessibility_indices) AS u(grid_id, accessibility_index)
				GROUP BY u.grid_id, x.amenity, x.name
				
			) s
			GROUP BY s.grid_id
		)
		SELECT n.grid_id, n.accessibility_index
		FROM null_grids n 
		LEFT JOIN grouped_grids g
		ON n.grid_id = g.grid_id 
		WHERE g.grid_id IS NULL
		UNION ALL 
		SELECT * FROM grouped_grids; 
	END IF;
END;
$function$;
/*
SELECT h.*, g.geom  
FROM heatmap_dynamic('{"kindergarten":{"sensitivity":250000,"weight":1}}'::jsonb,'default',7533184,1) h, grid_heatmap g
WHERE h.grid_id = g.grid_id 
*/

/*
Next steps:
- Other population - walkability
- Isochrone calculation heatmap
- Test pgrouting_edges_heatmap with ways scenario
- Implement heatmap scenario, comparison
- Testing
*/