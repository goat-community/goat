DROP FUNCTION IF EXISTS compute_area_isochrone;
CREATE OR REPLACE FUNCTION compute_area_isochrone(grid_id_input integer, scenario_id_input integer DEFAULT 0)
  RETURNS SETOF VOID AS
$func$
DECLARE 
	var_area NUMERIC;
	iso_geom geometry;  
BEGIN 
	
	WITH x AS 
	(
		SELECT st_startpoint(geom) geom  
		FROM reached_edges_heatmap 
		WHERE gridids && ARRAY[grid_id_input]
		AND scenario_id = scenario_id_input 
		UNION ALL 
		SELECT st_endpoint(geom) geom  
		FROM reached_edges_heatmap 
		WHERE gridids && ARRAY[grid_id_input]
		AND scenario_id = scenario_id_input 
	), 
	convex AS 
	(
		SELECT ST_CONVEXHULL(ST_COLLECT(geom)) AS geom 
		FROM x 
	)
	SELECT ST_AREA(geom), geom
	INTO var_area, iso_geom
	FROM convex; 
	
	IF scenario_id_input = 0 THEN 
		UPDATE grid_heatmap SET area_isochrone = var_area
		WHERE grid_id = grid_id_input;
	ELSE 
		INSERT INTO area_isochrones_scenario(grid_id, area_isochrone, geom, scenario_id) 
		VALUES(grid_id_input,var_area,iso_geom,scenario_id_input);
	END IF;
END 	
$func$  LANGUAGE plpgsql;

/*SELECT compute_area_isochrone(1,0)*/

