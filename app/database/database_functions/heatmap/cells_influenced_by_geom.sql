-- Returns all cell ids that are within a specified radius of the input geometry
DROP FUNCTION IF EXISTS cells_influenced_by_geom;
CREATE FUNCTION cells_influenced_by_geom(userid_input integer, influencing_radius numeric) 
RETURNS SETOF integer AS
$BODY$
DECLARE
    buffer geometry;
BEGIN
	SELECT ST_BUFFER(ST_UNION(geom), influencing_radius)  
	INTO buffer
	FROM pois_userinput 
	WHERE userid = userid_input
	OR gid IN (SELECT UNNEST(ids_modified_features(userid_input,'pois')));

	RETURN query
    SELECT grid_id
   	FROM grid_500
   	WHERE ST_Intersects(buffer,geom);
END;
$BODY$ LANGUAGE plpgsql;
-- meters to degrees: 
-- 0.00001 * (100 / 111) * meters
-- 5 km/h in m/s times 900 seconds to get max walking distance 
-- (5 / 3.6) * 15 *60

-- 

--SELECT cells_influenced_by_geom((SELECT array_agg(geom) FROM pois_modified), 0.01126126)

