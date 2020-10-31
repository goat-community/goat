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
  	SELECT CASE WHEN c.fraction = 0 THEN ST_STARTPOINT(ST_LINESUBSTRING(c.geom,0,0.000001))
  	WHEN c.fraction = 1 THEN ST_ENDPOINT(ST_LINESUBSTRING(c.geom,0.999999,1))
  	ELSE c.closest_point END AS closest_point, 
  	CASE WHEN c.fraction = 0 THEN 0.000001
  	WHEN c.fraction = 1 THEN 0.999999
  	ELSE c.fraction END, c.vid, c.wid 
  	FROM closest_edge c;

END 
$function$;



/*
Some testing
SELECT ST_LineLocatePoint( st_geomfromtext('LINESTRING(11.2400 48.1831,11.24 48.1839993299747)'),st_geomfromtext('POINT(11.2401 48.1835)')) AS fraction

SELECT ST_LineLocatePoint( st_geomfromtext('LINESTRING(11.24 48.18381946399108,11.2400 48.1831)'),st_geomfromtext('POINT(11.2401 48.1835)')) AS fraction

/*Long line*/

SELECT ST_LENGTH(ST_geomfromtext('LINESTRING (11.2365658 48.1837102, 11.2370149 48.1844426, 11.2371337 48.1844599, 11.239785 48.1832938, 11.240019 48.1831551, 11.2401638 48.1830066, 11.2403495 48.1826575, 11.240472 48.182499, 11.2405917 48.1824167)'))

len = 0.00509601984753803
pos = 0.819029850124106
fraction_1 = 0.004173792371958542
fraction_2 = 0.000922227475579488

SELECT ST_LINELOCATEPOINT(ST_geomfromtext('LINESTRING (11.2365658 48.1837102, 11.2370149 48.1844426, 11.2371337 48.1844599, 11.239785 48.1832938, 11.240019 48.1831551, 11.2401638 48.1830066, 11.2403495 48.1826575, 11.240472 48.182499, 11.2405917 48.1824167)'),
ST_GEOMFROMTEXT('POINT(11.2400 48.1831)'))

/*Short line*/

SELECT ST_LENGTH(ST_geomfromtext('LINESTRING (11.239412971922341 48.183457426123546, 11.239785 48.1832938, 11.240019 48.1831551, 11.2401638 48.1830066, 11.2403495 48.1826575, 11.240472 48.182499, 11.2405917 48.1824167)'))

len = 0.0016268522004702437
pos = 0.43312153660122477
fraction_1 = 0.000704624724890755713690039360376449
fraction_2 = 0.000922227475579487986309960639623551


*/