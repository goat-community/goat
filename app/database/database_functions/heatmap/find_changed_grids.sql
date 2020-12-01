-- Returns all cell ids that are within a specified radius of the input geometry
DROP FUNCTION IF EXISTS find_changed_grids;
CREATE FUNCTION find_changed_grids(scenario_id_input integer, influencing_radius numeric) 
RETURNS TABLE (starting_points float[][],gridids integer[]) AS 
$BODY$
DECLARE 
	proj_radius numeric;
BEGIN

	DROP TABLE IF EXISTS buffer_points;
	CREATE TEMP TABLE buffer_points AS 
	WITH deleted_geoms AS 
	(
		SELECT geom 
		FROM ways_userinput wu 
		WHERE id IN (SELECT UNNEST(deleted_ways) FROM scenarios WHERE scenario_id = scenario_id_input)
	)
	SELECT geom 
	FROM ways_userinput_vertices_pgr v 
	WHERE scenario_id = scenario_id_input
	UNION ALL 
	SELECT st_startpoint(geom)
	FROM ways_modified 
	WHERE scenario_id = scenario_id_input 
	UNION ALL 
	SELECT st_endpoint(geom)
	FROM ways_modified 
	WHERE scenario_id = scenario_id_input
	UNION ALL 
	SELECT st_startpoint(geom)
	FROM deleted_geoms 
	UNION ALL 
	SELECT st_endpoint(geom)
	FROM deleted_geoms;
	
	proj_radius = (SELECT ST_LENGTH(ST_MAKELINE(geom,ST_Project(geom::geography, influencing_radius, radians(45.0))::geometry)) FROM buffer_points LIMIT 1);
	
	DROP TABLE IF EXISTS buffer;
	CREATE TABLE buffer AS 
	SELECT (ST_DUMP(ST_UNION(ST_BUFFER(ST_QuantizeCoordinates(b.geom,3),proj_radius)))).geom AS geom	
	FROM buffer_points b;
	
	CREATE INDEX ON buffer USING GIST(geom);

	RETURN query
	SELECT DISTINCT ARRAY_AGG(ARRAY[ST_X(st_centroid(g.geom))::float,ST_Y(ST_Centroid(g.geom))::float]) starting_points, array_agg(g.grid_id) AS grid_ids
	FROM buffer b, grid_heatmap g
	WHERE ST_Intersects(b.geom,g.geom);

END;
$BODY$ LANGUAGE plpgsql;
/*SELECT * FROM find_changed_grids(1,1000)*/