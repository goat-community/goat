
-- Returns all cell ids that are within a specified radius of the input geometry
DROP FUNCTION IF EXISTS find_changed_grids;
CREATE FUNCTION find_changed_grids(scenario_id_input integer, influencing_radius numeric) 
RETURNS TABLE (section_id integer, starting_points float[][],gridids integer[], geom geometry) AS 
$BODY$
DECLARE 
	proj_radius numeric;
BEGIN

	DROP TABLE IF EXISTS buffer_points;
	CREATE TEMP TABLE buffer_points AS 
	WITH deleted_geoms AS 
	(
		SELECT w.geom 
		FROM ways_userinput w
		WHERE id IN (SELECT UNNEST(deleted_ways) FROM scenarios WHERE scenario_id = scenario_id_input)
	)
	SELECT v.geom 
	FROM ways_userinput_vertices_pgr v 
	WHERE scenario_id = scenario_id_input
	UNION ALL 
	SELECT st_startpoint(w.geom)
	FROM ways_modified w
	WHERE scenario_id = scenario_id_input 
	UNION ALL 
	SELECT st_endpoint(w.geom)
	FROM ways_modified w
	WHERE scenario_id = scenario_id_input
	UNION ALL 
	SELECT st_startpoint(d.geom)
	FROM deleted_geoms d
	UNION ALL 
	SELECT st_endpoint(d.geom)
	FROM deleted_geoms d;
	
	proj_radius = (SELECT ST_LENGTH(ST_MAKELINE(b.geom,ST_Project(b.geom::geography, influencing_radius, radians(45.0))::geometry)) FROM buffer_points b LIMIT 1);
	
	DROP TABLE IF EXISTS buffer;
	CREATE TEMP TABLE buffer AS 
	SELECT (ST_DUMP(ST_UNION(ST_BUFFER(ST_QuantizeCoordinates(b.geom,3),proj_radius)))).geom AS geom	
	FROM buffer_points b;
	
	CREATE INDEX ON buffer USING GIST(geom);

	RETURN query
	SELECT g.section_id::integer, ARRAY_AGG(g.starting_points)::float[][] AS starting_points, ARRAY_AGG(g.grid_id) AS grid_ids, b.geom 
	FROM buffer b, grid_ordered g 
	WHERE ST_Intersects(b.geom,g.centroid)
	GROUP BY g.section_id, b.geom;

END;
$BODY$ LANGUAGE plpgsql;
/*SELECT * FROM find_changed_grids(1,1600)*/