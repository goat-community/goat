DROP FUNCTION IF EXISTS heatmap_geoserver;
CREATE OR REPLACE FUNCTION public.heatmap_geoserver(amenities_json jsonb, modus_input text DEFAULT 'default', scenario_id_input integer DEFAULT 0)
 RETURNS TABLE(grid_id integer, percentile_accessibility integer, accessibility_index bigint, geom geometry)
 LANGUAGE plpgsql
AS $function$
DECLARE
	borders_quintiles bigint[]; 
BEGIN
	IF amenities_json::TEXT = '{}' OR modus_input NOT IN ('default','scenario','comparison') THEN 
		RETURN query 
		SELECT 0,0, 0::bigint,g.geom 
		FROM grid_heatmap g
		LIMIT 0;
		RETURN;
	END IF; 

	IF modus_input IN ('default','comparison') THEN   
		DROP TABLE IF EXISTS grids_default; 
		CREATE TEMP TABLE grids_default AS 
		SELECT g.grid_id, COALESCE(h.percentile_accessibility,0) AS percentile_accessibility, h.accessibility_index, g.geom  
		FROM grid_heatmap g
		LEFT JOIN (
			SELECT h.grid_id, ntile(5) over (order by h.accessibility_index) AS percentile_accessibility,
			h.accessibility_index
			FROM heatmap_dynamic(amenities_json,'default',scenario_id_input) h
			WHERE h.accessibility_index IS NOT NULL 
		) h
		ON g.grid_id = h.grid_id;	
	END IF; 
	
	IF modus_input IN ('scenario','comparison') THEN  
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
				WHERE h.accessibility_index IS NOT NULL
			) x 
			GROUP BY x.percentile_accessibility 
			ORDER BY x.percentile_accessibility
		) b;
	
		DROP TABLE IF EXISTS grids_scenario;
		CREATE TEMP TABLE grids_scenario AS 
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
			WHERE h.accessibility_index IS NOT NULL
		) h
		ON g.grid_id = h.grid_id;	
	
	END IF;
	
	IF modus_input = 'comparison' THEN 

		ALTER TABLE grids_default ADD PRIMARY KEY(grid_id);
		ALTER TABLE grids_scenario ADD PRIMARY KEY(grid_id);
		
		DROP TABLE IF EXISTS grids_comparison;
		CREATE TEMP TABLE grids_comparison AS 
		SELECT d.grid_id, (s.percentile_accessibility - d.percentile_accessibility ) AS percentile_accessibility, 
		COALESCE(s.accessibility_index - d.accessibility_index,0) AS accessibility_index, d.geom
		FROM grids_default d, grids_scenario s 
		WHERE d.grid_id = s.grid_id;
	
	END IF;
	
	IF modus_input = 'default' THEN 
		RETURN query 
		SELECT * FROM grids_default;
	ELSEIF modus_input = 'scenario' THEN 
		RETURN query 
		SELECT * FROM grids_scenario;
	ELSEIF modus_input = 'comparison' THEN 
		RETURN query 
		SELECT * FROM grids_comparison;
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
