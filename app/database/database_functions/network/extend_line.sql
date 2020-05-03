DROP FUNCTION IF EXISTS extend_line;
CREATE OR REPLACE FUNCTION extend_line(geom geometry, extend_distance numeric)
RETURNS SETOF geometry 
LANGUAGE plpgsql
AS $function$
DECLARE
	start_geom geometry; 
	end_geom geometry;
	azimuth_A float;
	azimuth_B float;
	length_A NUMERIC;
	length_B NUMERIC;
	newpoint_A geometry;
	newpoint_B geometry;
BEGIN 
		
	-- get the points A and B given a line L
	start_geom = ST_STARTPOINT(geom);
	end_geom = ST_ENDPOINT(geom);
		
	-- Start line section
	azimuth_A = ST_AZIMUTH(ST_POINTN(geom,2),start_geom);

	-- End line section 
	azimuth_B = ST_AZIMUTH(ST_POINTN(geom,-2),end_geom);
	
	-- get the length of the line A --> B
	length_A = ST_DISTANCE(ST_STARTPOINT(geom),ST_POINTN(geom,2));
	length_B = ST_DISTANCE(ST_ENDPOINT(geom),ST_POINTN(geom,-2));
	
	newpoint_A = ST_TRANSLATE(start_geom, sin(azimuth_A) * extend_distance, cos(azimuth_A) * extend_distance);
	newpoint_B = ST_TRANSLATE(end_geom, sin(azimuth_B) * extend_distance, cos(azimuth_B) * extend_distance);

	RETURN query SELECT st_addpoint(st_addpoint(geom,newpoint_B),newpoint_A,0);
END
$function$

--1 meter in Germany approx. 0.0000127048
--SELECT extend_line(geom, 0.0000127048) FROM ways_modified WHERE id = 5;
