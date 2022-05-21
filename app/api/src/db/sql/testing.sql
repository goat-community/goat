/*
Nested array by grids by sensitvity
Return all gridsids also those that are not in directly in study area
*/





DROP FUNCTION IF EXISTS heatmap_dynamic;

SELECT basic.poi_categories(4) -> 'true'


SELECT basic.select_customization('heatmap_sensitivities')

SELECT ARRAY[1,2,3] # 2

CREATE EXTENSION intarray;

SELECT ARRAY_AGG(s.sensitivity::integer) 
FROM (
	SELECT jsonb_array_elements_text(basic.select_customization('heatmap_sensitivities')) sensitivity 
) s


DROP TABLE default_;
CREATE TABLE default_ AS

EXPLAIN ANALYZE 

SELECT grid_id, accessibility_index  
FROM basic.heatmap_local_accessibility('{"kindergarten":{"sensitivity":250000,"weight":1}, "bus_stop":{"sensitivity":250000,"weight":1}, "pub":{"sensitivity":350000,"weight":1}}'::jsonb, 4, 1, 'default',10) h

CREATE TABLE reached_poi_test AS 
SELECT poi_uid, ARRAY_AGG(COST) AS costs, array_agg(accessibility_index) accessibility_indices, 
array_agg(grid_visualization_id) grid_visualization_ids  
FROM customer.reached_poi_heatmap rph 
GROUP BY poi_uid, scenario_id  

ALTER TABLE reached_poi_test ADD COLUMN id serial; 

ALTER TABLE reached_poi_test ADD PRIMARY KEY(id);

GROUP BY grid_id 

DROP FUNCTION IF EXISTS basic.heatmap_local_accessibility 


SELECT *
FROM reached_poi_test 


CREATE OR REPLACE FUNCTION basic.heatmap_local_accessibility(amenities_json jsonb, user_id_input integer, active_study_area_id integer, modus_input text DEFAULT 'default', scenario_id_input integer DEFAULT 0, data_upload_ids integer[] DEFAULT '{}'::integer[])
 RETURNS TABLE(grid_id bigint, accessibility_index bigint)
 LANGUAGE plpgsql
AS $function$
DECLARE
	array_amenities text[];
	pois_one_entrance jsonb := basic.poi_categories(user_id_input) -> 'false';
	pois_more_entrances jsonb := basic.poi_categories(user_id_input) -> 'true';
	sensitivities integer[]; 
	translation_sensitivities jsonb;
	excluded_pois_id integer[];
BEGIN
  	
	SELECT ARRAY_AGG(s.sensitivity::integer) 
	INTO sensitivities 
	FROM (
		SELECT jsonb_array_elements_text(basic.select_customization('heatmap_sensitivities')) sensitivity 
	) s;

	SELECT array_agg(_keys)
	INTO array_amenities
	FROM (SELECT jsonb_object_keys(amenities_json) _keys) x;
	
	SELECT jsonb_object_agg(k, (sensitivities  # (v ->> 'sensitivity')::integer)::smallint)
	INTO translation_sensitivities
	FROM jsonb_each(amenities_json) AS u(k, v);

	RAISE NOTICE '%', sensitivities;
	RAISE NOTICE '%', array_amenities;
	RAISE NOTICE '%', translation_sensitivities; 
	RAISE NOTICE '%', pois_one_entrance;
	RAISE NOTICE '%', pois_more_entrances;


	
	--IF modus_input = 'default' THEN 
		
		RETURN query
		SELECT r.grid_visualization_id, SUM(r.accessibility_index[(translation_sensitivities ->> category)::integer]) AS accessibility_index 
		FROM customer.reached_poi_heatmap r, basic.grid_visualization g, basic.study_area_grid_visualization s, basic.poi p
		WHERE r.grid_visualization_id = g.id 
		AND r.grid_visualization_id = s.grid_visualization_id 
		AND s.study_area_id = active_study_area_id 
		AND p.uid = r.poi_uid 
		AND p.category IN (SELECT UNNEST(array_amenities))
		AND p.category IN (SELECT jsonb_array_elements_text(pois_one_entrance))
		GROUP BY r.grid_visualization_id;  

	
		RETURN query
		SELECT r.grid_visualization_id, SUM(r.accessibility_index[(translation_sensitivities ->> category)::integer]) AS accessibility_index 
		FROM customer.reached_poi_heatmap r, basic.grid_visualization g, basic.study_area_grid_visualization s, basic.poi p
		WHERE r.grid_visualization_id = g.id 
		AND r.grid_visualization_id = s.grid_visualization_id 
		AND s.study_area_id = active_study_area_id 
		AND p.uid = r.poi_uid 
		AND p.category IN (SELECT UNNEST(array_amenities))
		AND p.category IN (SELECT jsonb_array_elements_text(pois_more_entrances))
		GROUP BY r.grid_visualization_id;  
		/*
		UNION ALL 
		
		SELECT r.grid_visualization_id, max(accessibility_index[1]) AS accessibility_index 
		FROM customer.reached_poi_heatmap r, basic.grid_visualization g, basic.study_area_grid_visualization s, basic.poi p
		WHERE r.grid_visualization_id = g.id 
		AND r.grid_visualization_id = s.grid_visualization_id 
		AND s.study_area_id = active_study_area_id 
		AND p.uid = r.poi_uid 
		AND p.category IN (SELECT UNNEST(array_amenities))
		AND p.category IN (SELECT jsonb_array_elements_text(pois_more_entrances))
		GROUP BY r.grid_visualization_id;  
		*/
	--END IF; 
		

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

SELECT '''' ||column_name
|| ''''  
FROM information_schema.columns
 WHERE table_schema = 'basic'
   AND table_name   = 'edge'

   


		RETURN query 
		
	
		SELECT s.grid_id, sum(s.accessibility_index) AS accessibility_index 
		FROM 
		(
			SELECT u.grid_id, u.accessibility_index * (amenities_json -> x.amenity ->> 'weight')::SMALLINT AS accessibility_index  
			FROM (
				SELECT gridids, amenity, accessibility_indices[(translation_sensitivities ->> amenity)::integer:(translation_sensitivities ->> amenity)::integer][1:]
				FROM reached_pois_heatmap 
				WHERE amenity IN (SELECT jsonb_array_elements_text(pois_one_entrance))
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
	END IF; 


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
				SELECT u.grid_id, max(u.accessibility_index) * (amenities_json -> x.amenity ->> 'weight')::SMALLINT AS accessibility_index
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
		SELECT n.grid_id, n.accessibility_index
		FROM null_grids n 
		LEFT JOIN grouped_grids g
		ON n.grid_id = g.grid_id 
		WHERE g.grid_id IS NULL
		UNION ALL 
		SELECT * FROM grouped_grids; 
	END IF;



SELECT h.*, g.geom  
FROM heatmap_dynamic('{"kindergarten":{"sensitivity":250000,"weight":1}}'::jsonb,'default',13) h, grid_heatmap g
WHERE h.grid_id = g.grid_id; 


