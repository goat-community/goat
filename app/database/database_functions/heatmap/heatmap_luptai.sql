DROP FUNCTION IF EXISTS heatmap_luptai;
CREATE OR REPLACE FUNCTION public.heatmap_luptai(amenities_json jsonb, modus_input text DEFAULT 'default', scenario_id_input integer DEFAULT 0)
 RETURNS TABLE(grid_id integer, accessibility_index bigint, percentile_accessibility integer, percentile_population integer,
 population_accessibility integer, geom geometry)
 LANGUAGE plpgsql
AS $function$
BEGIN
	IF amenities_json::TEXT <> '{}' AND modus_input <> 'comparison' THEN  
		RETURN query 
		SELECT h.grid_id, h.accessibility_index, h.percentile_accessibility, p.percentile_population, 
		(p.percentile_population-h.percentile_accessibility) AS population_accessibility, h.geom  
		FROM heatmap_geoserver(amenities_json,modus_input,scenario_id_input) h, 
		population_heatmap(scenario_id_input, modus_input) p 
		WHERE p.grid_id = h.grid_id;
	
	ELSEIF amenities_json::TEXT <> '{}' AND modus_input = 'comparison' THEN 
		RAISE NOTICE '%', 'comparison';
		DROP TABLE IF EXISTS luptai_default; 
		CREATE TEMP TABLE luptai_default AS 
		SELECT h.grid_id, h.accessibility_index, h.percentile_accessibility, p.percentile_population, 
		(p.percentile_population-h.percentile_accessibility) AS population_accessibility, h.geom  
		FROM heatmap_geoserver(amenities_json,'default',scenario_id_input) h, 
		population_heatmap(scenario_id_input, 'default') p 
		WHERE p.grid_id = h.grid_id;
		ALTER TABLE luptai_default ADD PRIMARY KEY(grid_id);
		
		DROP TABLE IF EXISTS luptai_scenario;
		CREATE TEMP TABLE luptai_scenario AS 
		SELECT h.grid_id, h.accessibility_index, h.percentile_accessibility, p.percentile_population, 
		(p.percentile_population-h.percentile_accessibility) AS population_accessibility, h.geom  
		FROM heatmap_geoserver(amenities_json,'scenario',scenario_id_input) h, 
		population_heatmap(scenario_id_input,'scenario') p 
		WHERE p.grid_id = h.grid_id;
		ALTER TABLE luptai_scenario ADD PRIMARY KEY(grid_id);
	
		RETURN query
		SELECT d.grid_id, NULL::bigint AS accessibility_index, NULL::integer AS percentile_accessibility, NULL::integer AS percentile_population, 
		CASE WHEN d.population_accessibility <> s.population_accessibility 
		THEN abs(d.population_accessibility) - abs(s.population_accessibility)  
		ELSE 0 END AS population_accessibility, d.geom
		FROM luptai_default d, luptai_scenario s
		WHERE d.grid_id = s.grid_id;
	
	END IF; 
END
$function$;

/*
SELECT * FROM heatmap_luptai('{"nursery":{"sensitivity":250000,"weight":1}}'::jsonb, 'scenario', 6)
*/