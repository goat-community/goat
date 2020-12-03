DROP FUNCTION IF EXISTS recompute_heatmap;
CREATE OR REPLACE FUNCTION recompute_heatmap(userid_input integer, scenario_id_input integer)
  RETURNS SETOF VOID AS
$func$
DECLARE 
	speed NUMERIC := 1.33;
	max_cost NUMERIC := 1200.;
BEGIN 
	
	DELETE FROM reached_edges_heatmap 
	WHERE scenario_id = scenario_id_input;

	DELETE FROM area_isochrones_scenario
	WHERE scenario_id = scenario_id_input;
	
	DROP TABLE IF EXISTS changed_grids;
	CREATE TEMP TABLE changed_grids AS 
	SELECT * FROM find_changed_grids(scenario_id_input,speed*max_cost);
	
	PERFORM public.pgrouting_edges_heatmap(ARRAY[max_cost], f.starting_points, speed, f.gridids, 2, 'walking_standard',userid_input, scenario_id_input,0)
	FROM changed_grids f;
	
	PERFORM compute_area_isochrone(UNNEST(gridids),scenario_id_input)
	FROM changed_grids;
	
	
END 	
$func$  LANGUAGE plpgsql;

/*SELECT recompute_heatmap(2,2)*/