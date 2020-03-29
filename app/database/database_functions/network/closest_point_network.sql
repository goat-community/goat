DROP FUNCTION IF EXISTS closest_point_network;
CREATE OR REPLACE FUNCTION closest_point_network(x NUMERIC, y NUMERIC)
RETURNS TABLE(closest_point geometry, fraction float, vid integer, wid integer)
 LANGUAGE plpgsql
AS $function$
DECLARE
	point geometry;	
BEGIN 
	point = ST_SETSRID(ST_POINT(x,y),4326);
	RETURN query
	SELECT ST_CLOSESTPOINT(geom,point) AS closest_point,ST_LineLocatePoint(geom,point) AS fraction, 
	999999999,w.id AS wid
	FROM temp_fetched_ways w
	WHERE St_buffer(point,0.0018) && geom
	ORDER BY ST_CLOSESTPOINT(geom,point) <-> point
  	LIMIT 1;

END 
$function$;


--SELECT * FROM closest_point_network(11.239410000,48.158710000)

