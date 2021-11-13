/*This function create two artificial edges at starting point */
DROP FUNCTION IF EXISTS create_artificial_edges;
CREATE OR REPLACE FUNCTION create_artificial_edges(sql_network TEXT, point geometry, snap_distance float)
RETURNS TABLE(wid integer, id integer, COST float, reverse_cost float, length_m float, SOURCE integer, target integer, geom geometry)
 LANGUAGE plpgsql
AS $function$
DECLARE
	sql_start_vertices TEXT; 
	rec record;
	line_part1 geometry;
	line_part2 geometry;
	length_part1 float;
	length_part2 float;
	line_part1_id integer; 
	line_part2_id integer; 
	max_id integer := 999999999;
	buffer geometry; 
BEGIN 
	
	buffer = ST_Buffer(point::geography, snap_distance)::geometry;
  	sql_start_vertices = 'SELECT ST_LineLocatePoint(geom,$2) AS fraction, 
	w.geom AS w_geom, w.length_m, w.SOURCE, w.target, w.COST, w.reverse_cost, $3 AS vid, w.id AS wid
	FROM 
	(
		%1$s	
	) w
	WHERE $1 && geom
	ORDER BY ST_CLOSESTPOINT(geom,$2) <-> $2
  	LIMIT 1;';
   
	EXECUTE format(sql_start_vertices, sql_network) USING buffer, point, max_id INTO rec;
 	
	line_part1 = ST_LINESUBSTRING(rec.w_geom,0,rec.fraction);
	line_part2 = ST_LINESUBSTRING(rec.w_geom,rec.fraction,1);
	length_part1 = ST_Length(line_part1::geography);
	length_part2 = rec.length_m - length_part1;
	line_part1_id = max_id;
	line_part2_id = max_id -1;

  	RETURN query 
	SELECT rec.wid, line_part1_id AS id, 
	rec.COST * (length_part1 / rec.length_m) AS COST,
	rec.reverse_cost * (length_part1 / rec.length_m) AS reverse_cost,
	length_part1, rec.SOURCE, rec.vid AS target, line_part1 AS geom
	UNION ALL
	SELECT rec.wid, line_part2_id AS id,
	rec.COST * (length_part2 / rec.length_m) AS COST,
	rec.reverse_cost * (length_part2 / rec.length_m) AS reverse_cost,
	length_part2, rec.vid AS SOURCE, rec.target, line_part2 AS geom; 
	
END 
$function$;

/*
 SELECT * 
FROM create_artificial_edges(
	fetch_ways_routing_v2(ST_ASTEXT(ST_BUFFER(ST_POINT(11.543274,48.195524),0.0018)),1,1,1.33,'walking_standard'),
	ST_SETSRID(ST_POINT(11.543274,48.195524), 4326), 0.0018
); 
 */