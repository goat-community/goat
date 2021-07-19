/*This function get the average slope using an IDW and an elevation dataset as points.*/
DROP FUNCTION IF EXISTS get_elevation_profile_vector;
CREATE OR REPLACE FUNCTION get_elevation_profile_vector(way_geom geometry, length_meters float, translation_m_degree float, interval_ float default 10)
	RETURNS TABLE (elev float, len float)
	LANGUAGE plpgsql
AS $function$
DECLARE 
	length_degree NUMERIC;
BEGIN

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
	
	RETURN QUERY 
	WITH points AS 
	(
		SELECT ROW_NUMBER() OVER() cnt, x.geom, x.len 
		FROM (
			SELECT st_startpoint(way_geom) AS geom, interval_ AS len
			UNION ALL 
			SELECT geom, interval_ AS len FROM dump_points
			UNION ALL 
			SELECT st_endpoint(way_geom), (length_meters - floor((length_meters / interval_)) * interval_) AS len   
		) x
	), 
	elevs AS 
	(
		SELECT cnt AS gid, p.geom, SUM(idw.val/(idw.distance/translation_m_degree))/SUM(1/(idw.distance/translation_m_degree))::real AS elev, p.len
		FROM points p
		CROSS JOIN LATERAL 
		(
			SELECT d.val, ST_DISTANCE(p.geom, d.geom) AS distance
			FROM dem_vec d 
			WHERE ST_DWITHIN(p.geom, d.geom, translation_m_degree * 25)
			ORDER BY p.geom <-> d.geom
			LIMIT 3		
		) idw
		WHERE p.geom IS NOT NULL 
		GROUP BY cnt, p.geom, p.len 
		ORDER BY cnt
	) 	
	SELECT e.elev, e.len
	FROM elevs e;

END;
$function$;

/*
CREATE TABLE dem_vec AS 
SELECT c.geom, c.val  
FROM dem, LATERAL ST_PixelAsCentroids(rast) c;
CREATE INDEX ON dem_vec USING GIST(geom);

DROP TABLE test; 
CREATE TABLE test AS 
SELECT x.id, x.geom, abs(slope) * 100 AS slope 
FROM (SELECT * FROM footpath_visualization f LIMIT 10000) x, get_elevation_profile_vector(geom, length_m, meter_degree(),10) slope 
 */