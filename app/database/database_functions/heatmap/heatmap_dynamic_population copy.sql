DROP FUNCTION IF EXISTS heatmap_dynamic_population_test;
CREATE OR REPLACE FUNCTION public.heatmap_dynamic_population_test(amenities_json jsonb, population_json jsonb, modus_input text DEFAULT 'default', scenario_id_input integer DEFAULT 0)
 RETURNS TABLE(grid_id integer, accessibility_index bigint, ai_pop float)
 LANGUAGE plpgsql
AS $function$
DECLARE
	array_amenities text[];
	pois_one_entrance text[] := select_from_variable_container('pois_one_entrance');
	pois_more_entrances text[] := select_from_variable_container('pois_more_entrances');
	sensitivities integer[] := select_from_variable_container('heatmap_sensitivities')::integer[];
	translation_sensitivities jsonb;
	excluded_pois_id integer[];
	;
BEGIN
  	
	SELECT array_agg(_keys)
	INTO array_amenities
	FROM (SELECT jsonb_object_keys(amenities_json) _keys) x;
	
	SELECT jsonb_object_agg(k, (sensitivities  # (v ->> 'sensitivity')::integer)::smallint)
	INTO translation_sensitivities
	FROM jsonb_each(amenities_json) AS u(k, v);

	/*IF modus_input = 'default' THEN*/
		RETURN query 
		select y.grid_id, sum(y.accessibility_index*(1)) as accessibility_index, sum(y.ai_pop*(1)) as accessibility_index_population from
		(SELECT x.gid, u.grid_id, x.amenity, u.accessibility_index::SMALLINT AS accessibility_index, u.accessibility_index / z.ai_pop::FLOAT(16) AS ai_pop  
			FROM (
				SELECT gid, gridids, amenity, accessibility_indices[(translation_sensitivities ->> amenity)::integer:(translation_sensitivities ->> amenity)::integer][1:]
				FROM reached_pois_heatmap 
				WHERE amenity IN (SELECT UNNEST(pois_one_entrance))
				AND amenity IN (SELECT UNNEST(array_amenities))
				AND scenario_id = 0
			)x, UNNEST(x.gridids, x.accessibility_indices) AS u(grid_id, accessibility_index),
			(select p.gid, sum(p.accessibility_pop) as ai_pop from (
				select r.gid, r.gridid, r.accessibility_index*g.population as accessibility_pop from (
				select gid, unnest(gridids) as gridid, unnest(accessibility_indices[(translation_sensitivities ->> amenity)::integer:(translation_sensitivities ->> amenity)::integer][1:]) as accessibility_index from reached_pois_heatmap 
				WHERE amenity IN (SELECT UNNEST(pois_one_entrance))
				AND amenity IN (SELECT UNNEST(array_amenities))
				AND scenario_id = 0) r,
				grid_heatmap g where r.gridid = g.grid_id and g.population > 0) p group by p.gid) z
		where x.gid = z.gid) y group by y.grid_id;
		/*SELECT s.grid_id, s.amenity, sum(s.accessibility_index) AS accessibility_index 
		FROM 
		(
			SELECT u.grid_id, x.amenity, u.accessibility_index * (amenities_json -> x.amenity ->> 'weight')::SMALLINT AS accessibility_index  
			FROM (
				SELECT gridids, amenity, accessibility_indices[(translation_sensitivities ->> amenity)::integer:(translation_sensitivities ->> amenity)::integer][1:]
				FROM reached_pois_heatmap 
				WHERE amenity IN (SELECT UNNEST(pois_one_entrance))
				AND amenity IN (SELECT UNNEST(array_amenities))
				AND scenario_id = 0
			)x, UNNEST(x.gridids, x.accessibility_indices) AS u(grid_id, accessibility_index)
			UNION ALL 
			SELECT u.grid_id, x.amenity, max(u.accessibility_index) * (amenities_json -> x.amenity ->> 'weight')::SMALLINT AS accessibility_index
			FROM (
				SELECT gridids, amenity, name,  accessibility_indices[(translation_sensitivities ->> amenity)::integer:(translation_sensitivities ->> amenity)::integer][1:]
				FROM reached_pois_heatmap
				WHERE amenity IN (SELECT UNNEST(pois_more_entrances))
				AND amenity IN (SELECT UNNEST(array_amenities))
				AND scenario_id = 0
			)x, UNNEST(x.gridids, x.accessibility_indices) AS u(grid_id, accessibility_index)
			GROUP BY u.grid_id, x.name, x.amenity
		) s
		GROUP BY s.grid_id, s.amenity;
	/*ELSE
		excluded_pois_id = ids_modified_features(scenario_id_input,'pois');
		RETURN query 
		WITH null_grids AS 
		(
			SELECT DISTINCT UNNEST(gridids) grid_id, amenity,0 accessibility_index
			FROM reached_pois_heatmap 
			WHERE gid IN (SELECT UNNEST(excluded_pois_id))
		),
		grouped_grids AS 
		(
			SELECT s.grid_id, s.amenity, sum(s.accessibility_index) AS accessibility_index 
			FROM 
			(
				SELECT u.grid_id, x.amenity, u.accessibility_index * (amenities_json -> x.amenity ->> 'weight')::SMALLINT AS accessibility_index  
				FROM (
					SELECT r.gridids, r.amenity, accessibility_indices[(translation_sensitivities ->> amenity)::integer:(translation_sensitivities ->> amenity)::integer][1:]
					FROM reached_pois_heatmap r
					LEFT JOIN 
					(	
						SELECT gid FROM reached_pois_heatmap 
						WHERE scenario_id = scenario_id_input 
						AND amenity IN (SELECT UNNEST(pois_one_entrance))
						AND amenity IN (SELECT UNNEST(array_amenities))
					) s
					ON r.gid = s.gid 
					WHERE s.gid IS NULL 
					AND r.scenario_id = 0
					AND amenity IN (SELECT UNNEST(pois_one_entrance))
					AND amenity IN (SELECT UNNEST(array_amenities))
					AND r.gid NOT IN (SELECT UNNEST(excluded_pois_id))
					UNION ALL 				
					SELECT gridids, amenity, accessibility_indices[(translation_sensitivities ->> amenity)::integer:(translation_sensitivities ->> amenity)::integer][1:]
					FROM reached_pois_heatmap 
					WHERE amenity IN (SELECT UNNEST(pois_one_entrance))
					AND amenity IN (SELECT UNNEST(array_amenities))
					AND scenario_id = scenario_id_input 
				)x, UNNEST(x.gridids, x.accessibility_indices) AS u(grid_id, accessibility_index)
				UNION ALL 
				SELECT u.grid_id, x.amenity, max(u.accessibility_index) * (amenities_json -> x.amenity ->> 'weight')::SMALLINT AS accessibility_index
				FROM (
					SELECT gridids, amenity, name, accessibility_indices[(translation_sensitivities ->> amenity)::integer:(translation_sensitivities ->> amenity)::integer][1:]
					FROM reached_pois_heatmap r
					LEFT JOIN 
					(
						SELECT gid 
						FROM reached_pois_heatmap 
						WHERE scenario_id = scenario_id_input
						AND amenity IN (SELECT UNNEST(pois_more_entrances))
						AND amenity IN (SELECT UNNEST(array_amenities))
					) s
					ON r.gid = s.gid 
					WHERE s.gid IS NULL
					AND r.scenario_id = 0
					AND amenity IN (SELECT UNNEST(array_amenities))
					AND amenity IN (SELECT UNNEST(pois_more_entrances))
					AND r.gid NOT IN (SELECT UNNEST(excluded_pois_id))
					UNION ALL 				
					SELECT gridids, amenity, name, accessibility_indices[(translation_sensitivities ->> amenity)::integer:(translation_sensitivities ->> amenity)::integer][1:]
					FROM reached_pois_heatmap 
					WHERE amenity IN (SELECT UNNEST(pois_more_entrances))
					AND amenity IN (SELECT UNNEST(array_amenities))
					AND scenario_id = scenario_id_input
				)x, UNNEST(x.gridids, x.accessibility_indices) AS u(grid_id, accessibility_index)
				GROUP BY u.grid_id, x.amenity, x.name	
			) s
			GROUP BY s.grid_id
		)
		SELECT n.grid_id, n.amenity, n.accessibility_index
		FROM null_grids n 
		LEFT JOIN grouped_grids g
		ON n.grid_id = g.grid_id 
		WHERE g.grid_id IS NULL
		UNION ALL 
		SELECT * FROM grouped_grids; 
	END IF;*/
END;
$function$;
/*
DROP TABLE scenario;
CREATE TABLE scenario AS 
SELECT h.*, g.geom  
FROM heatmap_dynamic('{"kindergarten":{"sensitivity":250000,"weight":1}}'::jsonb,'scenario',13) h, grid_heatmap g
WHERE h.grid_id = g.grid_id; 

DROP TABLE default_;
CREATE TABLE default_ AS 
SELECT h.*, g.geom  
FROM heatmap_dynamic('{"kindergarten":{"sensitivity":250000,"weight":1}}'::jsonb,'default',13) h, grid_heatmap g
WHERE h.grid_id = g.grid_id; 
*/



