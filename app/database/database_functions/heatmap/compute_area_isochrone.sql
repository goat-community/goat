DROP FUNCTION IF EXISTS compute_area_isochrone_pois;
CREATE OR REPLACE FUNCTION compute_area_isochrone_pois(gid_input integer, scenario_id_input integer, modus_input integer, userid_input integer)
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
	FROM reached_pois_heatmap r, pois p
	LATERAL isochrones_alphashape(userid_input, scenario_id_input, 15, ST_X(p.geom)::numeric, ST_Y(p.geom)::numeric, 
	3, 5, 0.00003, modus_input, objectid_input, 1, 'walking_standard') i 
	WHERE p.gid = gid_input and r.gid = p.gid;

	DELETE FROM edges WHERE objectid = 	objectid_input;

	IF scenario_id_input = 0 THEN 
		UPDATE pois SET area_isochrone = var_area
		WHERE gid = gid_input;
	ELSE 
		INSERT INTO area_isochrones_scenario(gid, area_isochrone, geom, scenario_id) 
		VALUES(gid_input,var_area,iso_geom,scenario_id_input);
	END IF;
END 	
$func$  LANGUAGE plpgsql;

/*SELECT compute_area_isochrone(g.grid_id,0,1,0)
FROM (SELECT grid_id FROM grid_heatmap LIMIT 100) g*/