DROP FUNCTION IF EXISTS heatmap_geoserver;
CREATE OR REPLACE FUNCTION public.heatmap_geoserver(amenities_json jsonb, modus_input integer DEFAULT 1, userid_input integer DEFAULT 0, scenario_id_input integer DEFAULT 0)
 RETURNS TABLE(grid_id integer, percentile_accessibility integer, accessibility_index bigint, geom geometry)
 LANGUAGE plpgsql
AS $function$

BEGIN
	IF amenities_json::TEXT <> '{}' THEN  
		RETURN query 
		SELECT g.grid_id, COALESCE(h.percentile_accessibility,0) AS percentile_accessibility, h.accessibility_index, g.geom  
		FROM grid_heatmap g
		LEFT JOIN (
			SELECT h.grid_id, ntile(5) over (order by h.accessibility_index) AS percentile_accessibility,
			h.accessibility_index
			FROM heatmap_dynamic(amenities_json,2,userid_input,1) h
		) h
		ON g.grid_id = h.grid_id;	
	ELSE 
		RETURN query 
		SELECT 0,0, 0::bigint,g.geom 
		FROM grid_heatmap g
		LIMIT 1;
	END IF; 
END;
$function$;


/*
SELECT *
FROM heatmap_geoserver('{"kindergarten":{"sensitivity":250000,"weight":1}}'::jsonb,2,1,1) 
*/