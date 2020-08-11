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
	WHERE ST_Buffer(point,0.0018) && geom
	ORDER BY ST_CLOSESTPOINT(geom,point) <-> point
  	LIMIT 1;

END 
$function$;


--SELECT * FROM closest_point_network(11.239410000,48.158710000)


DROP FUNCTION IF EXISTS closest_point_network_geom;
CREATE OR REPLACE FUNCTION closest_point_network_geom(point geometry)
RETURNS TABLE(closest_point geometry, fraction float, vid integer, wid integer)
 LANGUAGE plpgsql
AS $function$
BEGIN 

	RETURN query
	WITH closest_edge AS 
	(
		SELECT w.geom,ST_CLOSESTPOINT(geom,point) AS closest_point,ST_LineLocatePoint(geom,point) AS fraction, 
		999999999 vid, w.id AS wid
		FROM temp_fetched_ways w
		WHERE St_buffer(point,0.0018) && geom
		ORDER BY ST_CLOSESTPOINT(geom,point) <-> point
	  	LIMIT 1
  	)
  	SELECT CASE WHEN c.fraction = 0 THEN ST_STARTPOINT(ST_LINESUBSTRING(c.geom,0,0.001))
  	WHEN c.fraction = 1 THEN ST_ENDPOINT(ST_LINESUBSTRING(c.geom,0.999,1))
  	ELSE c.closest_point END AS closest_point, 
  	CASE WHEN c.fraction = 0 THEN 0.001
  	WHEN c.fraction = 1 THEN 0.999
  	ELSE c.fraction END, c.vid, c.wid 
  	FROM closest_edge c;

END 
$function$;



