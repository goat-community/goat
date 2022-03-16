DROP FUNCTION IF EXISTS basic.heatmap_local_accessibility;
CREATE OR REPLACE FUNCTION basic.heatmap_local_accessibility(amenities_json jsonb, user_id_input integer, active_study_area_id integer, modus_input text DEFAULT 'default', scenario_id_input integer DEFAULT 0, data_upload_ids integer[] DEFAULT '{}'::integer[])
 RETURNS TABLE(grid_visualization_id bigint, percentile_accessibility integer, accessibility_index bigint, modus text, geom geometry)
 LANGUAGE plpgsql
AS $function$
DECLARE
	borders_quintiles bigint[]; 
BEGIN
	
	
	DROP TABLE IF EXISTS heatmap_default; 
	CREATE TEMP TABLE heatmap_default AS
	WITH grouped AS 
	(
		SELECT h.grid_visualization_id, sum(h.accessibility_index) AS accessibility_index 
		FROM basic.prepare_heatmap_local_accessibility(amenities_json, user_id_input, active_study_area_id, 'default', scenario_id_input, data_upload_ids) h
		GROUP BY h.grid_visualization_id 	
	)
	SELECT g.id AS grid_visualization_id, 
	COALESCE(h.percentile_accessibility,0) AS percentile_accessibility, COALESCE(h.accessibility_index, 0)::bigint AS accessibility_index, 'default' AS modus, g.geom  
	FROM basic.grid_visualization g
	LEFT JOIN (
		SELECT h.grid_visualization_id, ntile(5) over (order by h.accessibility_index) AS percentile_accessibility, h.accessibility_index 
		FROM grouped h
		WHERE h.accessibility_index IS NOT NULL 
	) h
	ON g.id = h.grid_visualization_id;	
	
	IF modus_input IN ('scenario','comparison') THEN  
		SELECT array_agg(border)
		INTO borders_quintiles
		FROM 
		(
			SELECT min(h.accessibility_index) border
			FROM heatmap_default h
			WHERE h.accessibility_index <> 0
			GROUP BY h.percentile_accessibility 
			ORDER BY h.percentile_accessibility
		) b;
		
		RAISE NOTICE '%', borders_quintiles;  
		
		DROP TABLE IF EXISTS heatmap_scenario;
		CREATE TEMP TABLE heatmap_scenario AS 
		WITH grouped AS 
		(
			SELECT h.grid_visualization_id, sum(h.accessibility_index) AS accessibility_index 
			FROM basic.prepare_heatmap_local_accessibility(amenities_json, user_id_input, active_study_area_id, 'scenario', scenario_id_input, data_upload_ids) h
			GROUP BY h.grid_visualization_id 	
		),
		with_geom AS
		(
			SELECT g.id AS grid_visualization_id, COALESCE(h.accessibility_index, 0) AS accessibility_index, 'scenario' AS modus, g.geom  
			FROM basic.grid_visualization g
			LEFT JOIN grouped h 
			ON g.id = h.grid_visualization_id
		)		
		SELECT h.grid_visualization_id, 
		CASE WHEN h.accessibility_index = 0 THEN 0
		WHEN h.accessibility_index > 0 AND h.accessibility_index < borders_quintiles[2] THEN 1
		WHEN h.accessibility_index >= borders_quintiles[2] AND h.accessibility_index < borders_quintiles[3] THEN 2
		WHEN h.accessibility_index >= borders_quintiles[3] AND h.accessibility_index < borders_quintiles[4] THEN 3
		WHEN h.accessibility_index >= borders_quintiles[4] AND h.accessibility_index < borders_quintiles[5] THEN 4
		WHEN h.accessibility_index >= borders_quintiles[5] THEN 5
		END AS percentile_accessibility, h.accessibility_index::bigint, h.modus, h.geom  
		FROM with_geom h; 
	
	END IF; 
	
	IF modus_input = 'comparison' THEN 

		ALTER TABLE heatmap_default ADD PRIMARY KEY(grid_visualization_id);
		ALTER TABLE heatmap_scenario ADD PRIMARY KEY(grid_visualization_id);
		
		DROP TABLE IF EXISTS heatmap_comparison;
		CREATE TEMP TABLE heatmap_comparison AS 
		WITH with_geom AS  
		(
			SELECT d.grid_visualization_id, (s.percentile_accessibility - d.percentile_accessibility ) AS percentile_accessibility, 
			COALESCE(s.accessibility_index - d.accessibility_index,0) AS accessibility_index, 'comparison' AS modus, d.geom
			FROM heatmap_default d, heatmap_scenario s 
			WHERE d.grid_visualization_id = s.grid_visualization_id
		) 
		SELECT h.grid_visualization_id, ntile(10) over (order by h.accessibility_index) AS percentile_accessibility, h.accessibility_index, h.modus, h.geom  
		FROM with_geom h
		WHERE h.accessibility_index <> 0
		UNION ALL 
		SELECT h.grid_visualization_id, 0, h.accessibility_index, h.modus, h.geom   
		FROM with_geom h
		WHERE h.accessibility_index = 0; 
		
	END IF;


	IF modus_input = 'default' THEN 
		RETURN query 
		SELECT * 
		FROM heatmap_default;
	ELSEIF modus_input = 'scenario' THEN 
		RETURN query 
		SELECT * 
		FROM heatmap_scenario;
	ELSEIF modus_input = 'comparison' THEN 
		RETURN query 
		SELECT * 
		FROM heatmap_comparison;
	END IF; 
END
$function$;

/*
DROP TABLE IF EXISTS default_table; 
CREATE TABLE default_table AS 
SELECT * 
FROM basic.heatmap_local_accessibility('{"supermarket":{"sensitivity":250000,"weight":1}}'::jsonb, 4, 1, 'default',11, '{}'::integer[]) h;

DROP TABLE IF EXISTS scenario_table; 
CREATE TABLE scenario_table AS 
SELECT * 
FROM basic.heatmap_local_accessibility('{"supermarket":{"sensitivity":250000,"weight":1}}'::jsonb, 4, 1, 'scenario',11, '{}'::integer[]) h;

DROP TABLE IF EXISTS comparison_table; 
CREATE TABLE comparison_table AS 
SELECT * 
FROM basic.heatmap_local_accessibility('{"supermarket":{"sensitivity":250000,"weight":1}}'::jsonb, 4, 1, 'comparison',11, '{}'::integer[]) h;
*/