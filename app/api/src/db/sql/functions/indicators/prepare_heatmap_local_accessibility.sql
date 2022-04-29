CREATE OR REPLACE FUNCTION basic.prepare_heatmap_local_accessibility(amenities_json jsonb, user_id_input integer, active_study_area_id integer, modus_input text DEFAULT 'default', scenario_id_input integer DEFAULT 0, data_upload_ids integer[] DEFAULT '{}'::integer[])
 RETURNS TABLE(grid_visualization_id bigint, accessibility_index bigint)
 LANGUAGE plpgsql
AS $function$
DECLARE
	array_amenities text[];
	pois_one_entrance jsonb := basic.poi_categories(user_id_input) -> 'false';
	pois_more_entrances jsonb := basic.poi_categories(user_id_input) -> 'true';
	sensitivities integer[]; 
	translation_sensitivities jsonb;
	excluded_poi_uids text[] := '{}'::TEXT[];
BEGIN
  	
	SELECT ARRAY_AGG(s.sensitivity::integer) 
	INTO sensitivities 
	FROM (
		SELECT jsonb_array_elements_text(basic.select_customization('heatmap_sensitivities')) sensitivity 
	) s;

	SELECT jsonb_agg(a.category)
	INTO pois_one_entrance  
	FROM jsonb_object_keys(amenities_json) AS a(category), jsonb_array_elements_text(pois_one_entrance) AS o(category) 
	WHERE a.category = o.category; 
	
	SELECT jsonb_agg(a.category)
	INTO pois_more_entrances  
	FROM jsonb_object_keys(amenities_json) AS a(category), jsonb_array_elements_text(pois_more_entrances) AS o(category) 
	WHERE a.category = o.category; 

	SELECT jsonb_object_agg(k, (sensitivities  # (v ->> 'sensitivity')::integer)::smallint)
	INTO translation_sensitivities
	FROM jsonb_each(amenities_json) AS u(k, v);

	IF modus_input <> 'default' AND scenario_id_input <> 0 THEN 
		excluded_poi_uids = basic.modified_pois(scenario_id_input); 
	END IF; 

	RETURN query
	SELECT u.grid_visualization_id, (u.accessibility_index * (amenities_json -> x.category ->> 'weight')::SMALLINT)::bigint AS accessibility_index  
	FROM (
		SELECT grid_visualization_ids, accessibility_indices[(translation_sensitivities ->> p.category)::integer:(translation_sensitivities ->> p.category)::integer][1:], p.category
		FROM customer.reached_poi_heatmap r, basic.study_area s, basic.poi p   
		WHERE s.id = active_study_area_id 
		AND ST_Intersects(p.geom, s.buffer_geom_heatmap)
		AND p.uid = r.poi_uid 
		AND p.category IN (SELECT jsonb_array_elements_text(pois_one_entrance))
		AND p.uid NOT IN (SELECT UNNEST(excluded_poi_uids))
		AND r.scenario_id IS NULL 
	)x, UNNEST(x.grid_visualization_ids, x.accessibility_indices) AS u(grid_visualization_id, accessibility_index);

	RETURN query 
	SELECT u.grid_visualization_id, (max(u.accessibility_index) * (amenities_json -> x.category ->> 'weight')::SMALLINT)::bigint AS accessibility_index  
	FROM (
		SELECT grid_visualization_ids, accessibility_indices[(translation_sensitivities ->> p.category)::integer:(translation_sensitivities ->> p.category)::integer][1:], 
		p.category, p.name
		FROM customer.reached_poi_heatmap r, basic.study_area s, basic.poi p   
		WHERE s.id = active_study_area_id 
		AND ST_Intersects(p.geom, s.buffer_geom_heatmap)
		AND p.uid = r.poi_uid 
		AND r.scenario_id IS NULL
		AND p.uid NOT IN (SELECT UNNEST(excluded_poi_uids))
		AND p.category IN (SELECT jsonb_array_elements_text(pois_more_entrances))
	)x, UNNEST(x.grid_visualization_ids, x.accessibility_indices) AS u(grid_visualization_id, accessibility_index)
	GROUP BY u.grid_visualization_id, x.category, x.name;  
	
	IF data_upload_ids <> '{}'::integer[] THEN 
		RETURN query
		SELECT u.grid_visualization_id, (u.accessibility_index * (amenities_json -> x.category ->> 'weight')::SMALLINT)::bigint AS accessibility_index  
		FROM (
			SELECT grid_visualization_ids, accessibility_indices[(translation_sensitivities ->> p.category)::integer:(translation_sensitivities ->> p.category)::integer][1:], p.category
			FROM customer.reached_poi_heatmap r, basic.study_area s, customer.poi_user p   
			WHERE s.id = active_study_area_id 
			AND ST_Intersects(p.geom, s.buffer_geom_heatmap)
			AND p.uid = r.poi_uid 
			AND r.scenario_id IS NULL 
			AND p.category IN (SELECT jsonb_array_elements_text(pois_one_entrance))
			AND (p.uid NOT IN (SELECT UNNEST(excluded_poi_uids)) AND scenario_id IS NULL)
			AND p.data_upload_id IN (SELECT UNNEST(data_upload_ids))
		)x, UNNEST(x.grid_visualization_ids, x.accessibility_indices) AS u(grid_visualization_id, accessibility_index);
	
		RETURN query 
		SELECT u.grid_visualization_id, (max(u.accessibility_index) * (amenities_json -> x.category ->> 'weight')::SMALLINT)::bigint AS accessibility_index  
		FROM (
			SELECT grid_visualization_ids, accessibility_indices[(translation_sensitivities ->> p.category)::integer:(translation_sensitivities ->> p.category)::integer][1:], 
			p.category, p.name
			FROM customer.reached_poi_heatmap r, basic.study_area s, customer.poi_user p   
			WHERE s.id = active_study_area_id 
			AND ST_Intersects(p.geom, s.buffer_geom_heatmap)
			AND p.uid = r.poi_uid 
			AND r.scenario_id IS NULL 
			AND (p.uid NOT IN (SELECT UNNEST(excluded_poi_uids)) AND scenario_id IS NULL)
			AND p.category IN (SELECT jsonb_array_elements_text(pois_more_entrances))
			AND p.data_upload_id IN (SELECT UNNEST(data_upload_ids))
		)x, UNNEST(x.grid_visualization_ids, x.accessibility_indices) AS u(grid_visualization_id, accessibility_index)
		GROUP BY u.grid_visualization_id, x.category, x.name;  	
	END IF;

	IF modus_input <> 'default' AND scenario_id_input <> 0 THEN 
		RETURN query 
		SELECT u.grid_visualization_id, (u.accessibility_index * (amenities_json -> x.category ->> 'weight')::SMALLINT)::bigint AS accessibility_index  
		FROM (
			SELECT grid_visualization_ids, accessibility_indices[(translation_sensitivities ->> p.category)::integer:(translation_sensitivities ->> p.category)::integer][1:], p.category
			FROM customer.reached_poi_heatmap r, basic.study_area s, customer.poi_modified p  
			WHERE s.id = active_study_area_id 
			AND ST_Intersects(p.geom, s.buffer_geom_heatmap)
			AND p.uid = r.poi_uid 
			AND p.scenario_id = scenario_id_input 
			AND r.scenario_id = scenario_id_input
			AND p.edit_type <> 'd'
			AND p.category IN (SELECT jsonb_array_elements_text(pois_one_entrance))
		)x, UNNEST(x.grid_visualization_ids, x.accessibility_indices) AS u(grid_visualization_id, accessibility_index);
		
		RETURN query 
		SELECT u.grid_visualization_id, (max(u.accessibility_index) * (amenities_json -> x.category ->> 'weight')::SMALLINT)::bigint AS accessibility_index  
		FROM (
			SELECT grid_visualization_ids, accessibility_indices[(translation_sensitivities ->> p.category)::integer:(translation_sensitivities ->> p.category)::integer][1:], 
			p.category, p.name
			FROM customer.reached_poi_heatmap r, basic.study_area s, customer.poi_modified p   
			WHERE s.id = active_study_area_id 
			AND ST_Intersects(p.geom, s.buffer_geom_heatmap)
			AND p.uid = r.poi_uid 
			AND p.edit_type <> 'd'
			AND r.scenario_id = scenario_id_input
			AND p.scenario_id = scenario_id_input 
			AND p.category IN (SELECT jsonb_array_elements_text(pois_more_entrances))	
		)x, UNNEST(x.grid_visualization_ids, x.accessibility_indices) AS u(grid_visualization_id, accessibility_index)
		GROUP BY u.grid_visualization_id, x.category, x.name;  
	END IF; 
	
END;
$function$;

/*
DROP TABLE IF EXISTS default_heatmap;
CREATE TABLE default_heatmap AS 
WITH heatmap_grids AS 
(
	SELECT grid_visualization_id, sum(accessibility_index) 
	FROM basic.prepare_heatmap_local_accessibility('{"supermarket":{"sensitivity":250000,"weight":1}}'::jsonb, 4, 1, 'default',10) h
	GROUP BY grid_visualization_id 
)
SELECT h.*, g.geom 
FROM basic.grid_visualization g, heatmap_grids h 
WHERE h.grid_visualization_id = g.id;  

DROP TABLE IF EXISTS pois_to_explore; 
CREATE TABLE pois_to_explore AS 
SELECT * 
FROM basic.poi_aoi_visualization(4, 2, 'default', ARRAY[0], 1)
WHERE category = 'supermarket'
*/