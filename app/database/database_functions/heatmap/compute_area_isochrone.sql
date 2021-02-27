DROP FUNCTION IF EXISTS compute_area_isochrone;
CREATE OR REPLACE FUNCTION compute_area_isochrone(grid_id_input integer, scenario_id_input integer, modus_input integer, userid_input integer)
  RETURNS SETOF VOID AS
$func$
DECLARE 
	var_area NUMERIC;
	iso_geom geometry;  
	objectid_input integer;
BEGIN 
	
	objectid_input = random_between(1,900000000);

	SELECT avg(COALESCE(ST_AREA(i.geom),0))
	INTO var_area
	FROM grid_heatmap, 
	LATERAL isochrones_alphashape(userid_input, scenario_id_input, 15, ST_X(ST_CENTROID(geom))::numeric, ST_Y(ST_CENTROID(geom))::numeric, 
	3, 5, 0.00003, modus_input, objectid_input, 1, 'walking_standard') i 
	WHERE grid_id = grid_id_input;

	DELETE FROM edges WHERE objectid = 	objectid_input;

	IF scenario_id_input = 0 THEN 
		UPDATE grid_heatmap SET area_isochrone = var_area
		WHERE grid_id = grid_id_input;
	ELSE 
		INSERT INTO area_isochrones_scenario(grid_id, area_isochrone, geom, scenario_id) 
		VALUES(grid_id_input,var_area,iso_geom,scenario_id_input);
	END IF;
END 	
$func$  LANGUAGE plpgsql;

/*SELECT compute_area_isochrone(g.grid_id,0,1,0)
FROM (SELECT grid_id FROM grid_heatmap LIMIT 100) g*/