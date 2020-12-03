DROP FUNCTION IF EXISTS compute_area_isochrone;
CREATE OR REPLACE FUNCTION compute_area_isochrone(grid_id_input integer, scenario_id_input integer DEFAULT 0)
  RETURNS SETOF VOID AS
$func$
DECLARE 
	var_area NUMERIC;  
BEGIN 
	var_area = (SELECT DISTINCT ST_AREA(ST_CONVEXHULL(ST_COLLECT(geom))) AS area_isochrone
	FROM 
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
	) x);
	raise notice '%', var_area;
	IF scenario_id_input = 0 THEN 
		UPDATE grid_heatmap SET area_isochrone = var_area
		WHERE grid_id = grid_id_input;
	ELSE 
		INSERT INTO area_isochrones_scenario(grid_id, area_isochrone, scenario_id) 
		VALUES(grid_id_input,var_area,scenario_id_input);
	END IF;
END 	
$func$  LANGUAGE plpgsql;

/*SELECT compute_area_isochrone(1,0)*/