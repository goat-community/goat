CREATE OR REPLACE FUNCTION basic.create_perpendicular_line(line_geom geometry, point_geom geometry, length_line float)
  RETURNS SETOF geometry AS
$func$

	SELECT ST_SETSRID(
			ST_MAKELINE(
				ST_MAKEPOINT(x2+length_line,y2+(-1/((y2-y1)/(x2-x1)))*length_line), 
				ST_MAKEPOINT(x2-length_line,y2-(-1/((y2-y1)/(x2-x1)))*length_line)
			),4326)
	FROM (
		SELECT ST_X(st_startpoint(line_geom)) x1, ST_Y(st_startpoint(line_geom)) y1, ST_X(point_geom) x2, ST_Y(point_geom) y2 
	) x_y
$func$  LANGUAGE sql IMMUTABLE;