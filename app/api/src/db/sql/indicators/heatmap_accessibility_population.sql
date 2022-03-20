CREATE OR REPLACE FUNCTION basic.heatmap_accessibility_population(amenities_json jsonb, user_id_input integer, active_study_area_id integer, 
modus_input text DEFAULT 'default', scenario_id_input integer DEFAULT 0, data_upload_ids integer[] DEFAULT '{}'::integer[])
 RETURNS TABLE(grid_visualization_id bigint, accessibility_index bigint, percentile_accessibility integer, percentile_population integer, population_accessibility integer, modus text, geom geometry)
 LANGUAGE plpgsql
AS $function$
BEGIN
	
	IF modus_input IN ('default','scenario') THEN  
		RETURN query 
		SELECT h.grid_visualization_id, h.accessibility_index, h.percentile_accessibility, p.percentile_population, 
		(p.percentile_population-h.percentile_accessibility) AS population_accessibility, modus_input, h.geom  
		FROM basic.heatmap_local_accessibility(amenities_json, user_id_input, active_study_area_id, modus_input, scenario_id_input, data_upload_ids) h, 
		basic.heatmap_population(active_study_area_id, modus_input, scenario_id_input) p 
		WHERE p.grid_visualization_id = h.grid_visualization_id;
		
	ELSEIF modus_input = 'comparison' THEN 

		DROP TABLE IF EXISTS calc_default; 
		CREATE TEMP TABLE calc_default AS 
		SELECT h.grid_visualization_id, h.accessibility_index, h.percentile_accessibility, p.percentile_population, 
		(p.percentile_population-h.percentile_accessibility) AS population_accessibility, h.geom  
		FROM basic.heatmap_local_accessibility(amenities_json, user_id_input, active_study_area_id, 'default', scenario_id_input, data_upload_ids) h, 
		basic.heatmap_population(active_study_area_id, 'default', scenario_id_input) p 
		WHERE p.grid_visualization_id = h.grid_visualization_id;
		
		ALTER TABLE calc_default ADD PRIMARY KEY(grid_visualization_id);
		
		DROP TABLE IF EXISTS calc_scenario;
		CREATE TEMP TABLE calc_scenario AS 
		SELECT h.grid_visualization_id, h.accessibility_index, h.percentile_accessibility, p.percentile_population, 
		(p.percentile_population-h.percentile_accessibility) AS population_accessibility, h.geom  
		FROM basic.heatmap_local_accessibility(amenities_json, user_id_input, active_study_area_id, 'scenario', scenario_id_input, data_upload_ids) h, 
		basic.heatmap_population(active_study_area_id, 'scenario', scenario_id_input) p 
		WHERE p.grid_visualization_id = h.grid_visualization_id;
	
		ALTER TABLE calc_scenario ADD PRIMARY KEY(grid_visualization_id);
	
		RETURN query
		SELECT d.grid_visualization_id, NULL::bigint AS accessibility_index, NULL::integer AS percentile_accessibility, NULL::integer AS percentile_population, 
		CASE WHEN d.population_accessibility <> s.population_accessibility 
		THEN abs(d.population_accessibility) - abs(s.population_accessibility)  
		ELSE 0 END AS population_accessibility, modus_input, d.geom
		FROM calc_default d, calc_scenario s
		WHERE d.grid_visualization_id = s.grid_visualization_id;
	
	END IF; 
END
$function$;

/*
SELECT * 
FROM basic.heatmap_accessibility_population('{"supermarket":{"sensitivity":250000,"weight":1}}'::jsonb, 4, 1, 'comparison', 11, '{}'::integer[]) h;
*/