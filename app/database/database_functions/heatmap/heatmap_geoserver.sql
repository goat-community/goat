DROP FUNCTION IF EXISTS heatmap_geoserver;
CREATE OR REPLACE FUNCTION public.heatmap_geoserver(userid_input integer, amenities jsonb, modus_input int4)
  RETURNS SETOF type_heatmap
 LANGUAGE plpgsql
AS $function$
BEGIN 
	IF modus_input = 1 THEN 
		RETURN query
		SELECT g.grid_id, h.accessibility_index, 
		CASE WHEN h.accessibility_index <> 0 THEN ntile(5) over 
		(order by h.accessibility_index) ELSE 0 END AS percentile_accessibility, g.geom
		FROM grid_500 g
		LEFT JOIN 
		(
			SELECT grid_id, accessibility_index 
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
		    FROM heatmap_dynamic(userid_input,amenities,modus_input)
		), 
		joined AS (
			SELECT hs.grid_id,hs.accessibility_index
			FROM hs 
			LEFT JOIN hd 
			ON hs.grid_id = hd.grid_id
			WHERE hd.grid_id IS NULL 
			UNION ALL 
			SELECT hd.grid_id, accessibility_index FROM hd 
		)
		SELECT grid_id, accessibility_index, CASE WHEN accessibility_index <> 0 THEN ntile(5) over 
		(order by accessibility_index) ELSE 0 END AS percentile_accessibility, geom 
		FROM (
			SELECT g.grid_id, j.accessibility_index, g.geom
			FROM grid_500 g
			LEFT JOIN joined j
			ON g.grid_id = j.grid_id
		) x;
	ELSE 
		RAISE NOTICE 'Please insert a valid modus.';
	END IF; 
END;
$function$

/*
SELECT * 
FROM heatmap_geoserver(7833128, '{"kindergarten":{"sensitivity":250000,"weight":1},"bus_stop":{"sensitivity":250000,"weight":1}}'::jsonb,2)
*/
