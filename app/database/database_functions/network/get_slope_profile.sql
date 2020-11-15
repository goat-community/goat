CREATE OR REPLACE FUNCTION get_slope_profile(ways_id bigint, interval_ float default 10)
	RETURNS TABLE(elevs float[], linkLength float, lengthInterval float)
	LANGUAGE plpgsql
AS $function$
DECLARE 
	way_geom geometry;
	length_meters float;
	length_degree NUMERIC;
	translation_m_degree NUMERIC;
BEGIN
	
	SELECT geom, length_m, ST_Length(geom) 
	INTO way_geom, length_meters, length_degree
	FROM ways
	WHERE id = ways_id; 

	translation_m_degree = length_degree/length_meters;
	DROP TABLE IF EXISTS dump_points;
	IF length_meters > (2*interval_) THEN 
		CREATE TEMP TABLE dump_points AS 
		SELECT (ST_DUMP(ST_Lineinterpolatepoints(way_geom,interval_/length_meters))).geom AS geom;
	
	ELSEIF length_meters > interval_ AND length_meters < (2*interval_) THEN 
		CREATE TEMP TABLE dump_points AS 
		SELECT ST_LineInterpolatePoint(way_geom,0.5) AS geom;
		interval_ = length_meters/2;
	ELSE
		CREATE TEMP TABLE dump_points AS
		SELECT NULL::geometry AS geom;
	END IF;
		

	RETURN query
	WITH points AS 
	(
		SELECT ROW_NUMBER() OVER() cnt, geom, length_meters 
		FROM (
			SELECT st_startpoint(way_geom) AS geom
			UNION ALL 
			SELECT geom FROM dump_points
			UNION ALL 
			SELECT st_endpoint(way_geom) 
		) x
	)
	SELECT array_agg(elev) elevs, length_meters, interval_ 
	FROM 
	(
		SELECT SUM(idw.val/(idw.distance/translation_m_degree))/SUM(1/(idw.distance/translation_m_degree))::real AS elev
		FROM points p, get_idw_values(geom) idw
		WHERE p.geom IS NOT NULL 
		GROUP BY cnt 
		ORDER BY cnt 
	) x;

END;
$function$;

/*
EXPLAIN ANALYZE 
SELECT *
FROM get_slope_profile(266687)
*/