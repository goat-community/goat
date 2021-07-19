CREATE OR REPLACE FUNCTION get_idw_values(geom geometry)
RETURNS TABLE (dp_geom geometry, distance float, val float )
 LANGUAGE sql
AS $function$
	
	SELECT dp.geom, ST_DISTANCE(r.geom,dp.geom) distance, val
	FROM  
	(
		SELECT geom, st_clip(d.rast, st_buffer(geom, 0.00037135)) AS rast 	
		FROM dem d
		WHERE d.rast && st_buffer(geom, 0.00037135)
	) r
	, LATERAL ST_PixelAsCentroids(rast, 1) AS dp
	ORDER BY r.geom <-> dp.geom 
	LIMIT 3

$function$;