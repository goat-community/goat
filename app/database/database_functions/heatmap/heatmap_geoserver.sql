DROP FUNCTION IF EXISTS heatmap_geoserver;
CREATE OR REPLACE FUNCTION public.heatmap_geoserver(amenities_json jsonb, modus_input text DEFAULT 'default', scenario_id_input integer DEFAULT 0)
 RETURNS TABLE(grid_id integer, percentile_accessibility integer, accessibility_index bigint, geom geometry)
 LANGUAGE plpgsql
AS $function$
DECLARE
	borders_quintiles bigint[]; 
BEGIN
	IF amenities_json::TEXT <> '{}' AND modus_input = 'default' THEN  
		RETURN query 
		SELECT g.grid_id, COALESCE(h.percentile_accessibility,0) AS percentile_accessibility, h.accessibility_index, g.geom  
		FROM grid_heatmap g
		LEFT JOIN (
			SELECT h.grid_id, ntile(5) over (order by h.accessibility_index) AS percentile_accessibility,
			h.accessibility_index
			FROM heatmap_dynamic(amenities_json,'default',scenario_id_input) h
		) h
		ON g.grid_id = h.grid_id;	
	
	ELSEIF amenities_json::TEXT <> '{}' AND modus_input = 'scenario' THEN  
		SELECT array_agg(border)
		INTO borders_quintiles
		FROM 
		(
			SELECT min(x.accessibility_index) border
			FROM 
			(
				SELECT ntile(5) over (order by h.accessibility_index) AS percentile_accessibility,
				h.accessibility_index
				FROM heatmap_dynamic(amenities_json,'default',scenario_id_input) h
			) x 
			GROUP BY x.percentile_accessibility 
			ORDER BY x.percentile_accessibility
		) b;
	
		RAISE NOTICE '%', borders_quintiles;
	
		RETURN query 
		SELECT g.grid_id, 
		CASE WHEN COALESCE(h.accessibility_index,0) = 0 THEN 0
		WHEN COALESCE(h.accessibility_index,0) >= borders_quintiles[1] AND COALESCE(h.accessibility_index,0) < borders_quintiles[2] THEN 1
		WHEN COALESCE(h.accessibility_index,0) >= borders_quintiles[2] AND COALESCE(h.accessibility_index,0) < borders_quintiles[3] THEN 2
		WHEN COALESCE(h.accessibility_index,0) >= borders_quintiles[3] AND COALESCE(h.accessibility_index,0) < borders_quintiles[4] THEN 3
		WHEN COALESCE(h.accessibility_index,0) >= borders_quintiles[4] AND COALESCE(h.accessibility_index,0) < borders_quintiles[5] THEN 4
		WHEN COALESCE(h.accessibility_index,0) >= borders_quintiles[5] THEN 5
		END AS percentile_accessibility, h.accessibility_index, g.geom  
		FROM grid_heatmap g
		LEFT JOIN (
			SELECT h.grid_id, ntile(5) over (order by h.accessibility_index) AS percentile_accessibility,
			h.accessibility_index
			FROM heatmap_dynamic(amenities_json,modus_input,scenario_id_input) h
		) h
		ON g.grid_id = h.grid_id;	
	
	ELSEIF amenities_json::TEXT <> '{}' AND modus_input = 'comparison' THEN 
		DROP TABLE IF EXISTS grids_default; 
		CREATE TEMP TABLE grids_default AS 
		SELECT * FROM 
		heatmap_dynamic(amenities_json,'default',scenario_id_input);
		ALTER TABLE grids_default ADD PRIMARY KEY(grid_id);
		
		DROP TABLE IF EXISTS grids_scenario;
		CREATE TEMP TABLE grids_scenario AS 
		SELECT * FROM 
		heatmap_dynamic(amenities_json,'scenario',scenario_id_input);
		ALTER TABLE grids_scenario ADD PRIMARY KEY(grid_id);
		
		DROP TABLE IF EXISTS grids_comparison;
		CREATE TEMP TABLE grids_comparison AS 
		SELECT d.grid_id, COALESCE(s.accessibility_index,0) - d.accessibility_index AS difference
		FROM grids_default d
		LEFT JOIN grids_scenario s
		ON d.grid_id = s.grid_id
		UNION ALL 
		SELECT s.grid_id, s.accessibility_index AS difference
		FROM grids_scenario s
		LEFT JOIN grids_default d
		ON d.grid_id = s.grid_id
		WHERE d.grid_id IS NULL; 
		ALTER TABLE grids_comparison ADD PRIMARY KEY(grid_id);	
	
		RETURN query
		SELECT g.grid_id, 
		CASE WHEN h.accessibility_index < 0 AND h.accessibility_index IS NOT NULL 
		THEN -h.percentile_accessibility 
		WHEN h.accessibility_index > 0 AND h.accessibility_index IS NOT NULL 
		THEN h.percentile_accessibility 
		ELSE 0 END AS percentile_accessibility, h.accessibility_index, g.geom  
		FROM grid_heatmap g
		LEFT JOIN (
			SELECT c.grid_id, ntile(3) over (order by abs(c.difference)) AS percentile_accessibility, c.difference AS accessibility_index
			FROM grids_comparison c
			WHERE difference <> 0
		) h
		ON g.grid_id = h.grid_id;			
	ELSE 
		RETURN query 
		SELECT 0,0, 0::bigint,g.geom 
		FROM grid_heatmap g
		LIMIT 1;
	END IF; 
END
$function$;

/*
DROP TABLE test_default; 
CREATE TABLE test_default AS 
SELECT *
FROM heatmap_geoserver('{"nursery":{"sensitivity":250000,"weight":1}}'::jsonb,'default',47) 

DROP TABLE IF EXISTS test_scenario;
CREATE TABLE test_scenario AS 
SELECT *
FROM heatmap_geoserver('{"nursery":{"sensitivity":250000,"weight":1}}'::jsonb,'scenario',47) 

DROP TABLE IF EXISTS test_comparison;
CREATE TABLE test_comparison AS 
SELECT *
FROM heatmap_geoserver('{"nursery":{"sensitivity":250000,"weight":1}}'::jsonb,'comparison',47) 


*/