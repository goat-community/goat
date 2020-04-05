DROP FUNCTION IF EXISTS heatmap_geoserver;
CREATE OR REPLACE FUNCTION public.heatmap_geoserver(userid_input integer, amenities jsonb, modus_input int4)
  RETURNS SETOF type_heatmap
 LANGUAGE plpgsql
AS $function$
BEGIN 
	IF modus_input = 1 THEN 
		RETURN query
		SELECT g.grid_id, h.accessibility_index, COALESCE(percentile_accessibility,0)::smallint, g.percentile_population, g.geom
		FROM grid_500 g
		LEFT JOIN 
		(
			SELECT grid_id, accessibility_index, CASE WHEN accessibility_index <> 0 THEN ntile(5) over 
			(order by accessibility_index) ELSE 0 END AS percentile_accessibility 
			FROM heatmap(amenities)
		) h 
		ON g.grid_id = h.grid_id;
	
	ELSEIF modus_input = 2 THEN  
		RETURN query
		WITH hs AS(
			SELECT grid_id, accessibility_index 
			FROM heatmap(amenities)
		),
		hd AS (
			SELECT * 
		    FROM heatmap_dynamic(userid_input,amenities,2)
		), 
		joined AS (
			SELECT hs.grid_id,hs.accessibility_index
			FROM hs 
			LEFT JOIN hd 
			ON hs.grid_id = hd.grid_id
			WHERE hd.grid_id IS NULL 
			UNION ALL 
			SELECT hd.grid_id, accessibility_index FROM hd 
		),
		percentiles AS (
			SELECT grid_id, accessibility_index, CASE WHEN accessibility_index <> 0 THEN ntile(5) over 
			(order by accessibility_index) ELSE 0 END AS percentile_accessibility
			FROM joined 		
		)
		SELECT g.grid_id, p.accessibility_index, COALESCE(p.percentile_accessibility,0)::smallint AS percentile_accessibility, 
		g.percentile_population, g.geom
		FROM grid_500 g
		LEFT JOIN percentiles p
		ON g.grid_id = p.grid_id;
	ELSE 
		RAISE NOTICE 'Please insert a valid modus.';
	END IF; 
END;
$function$

/*
SELECT * 
FROM heatmap_geoserver(7833128, '{"kindergarten":{"sensitivity":250000,"weight":1},"bus_stop":{"sensitivity":250000,"weight":1}}'::jsonb,2)
*/
