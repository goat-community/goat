DROP FUNCTION IF EXISTS CalculateReachedPOIs;
CREATE OR REPLACE FUNCTION public.CalculateReachedPOIs(userid_input integer, reached_pois_table text, ids_calc int[])
RETURNS SETOF type_catchment_vertices_single
LANGUAGE plpgsql
AS $function$
DECLARE 
	id_calc integer;
	number_isochrones integer := 1;	
	alphashape_parameter_input NUMERIC := 0.00003;
	counter integer := 1;
BEGIN 
	
	EXECUTE format('DROP TABLE IF EXISTS '||reached_pois_table||';');
	EXECUTE format('CREATE TABLE '||reached_pois_table||'(cell_id int, object_id int, cost numeric, user_id int, scenario int, routing_method text, cost_sensitivity numeric, weighted_by_amenity numeric);');
		
	
	FOREACH id_calc IN ARRAY ids_calc
	LOOP 
		
		EXECUTE format('
			INSERT INTO '||reached_pois_table||' (SELECT closest_pois.cell_id AS cell_id, closest_pois.object_id as object_id, closest_pois.reached_cost AS cost
			FROM (
				SELECT * FROM closest_reached_pois(0.0009, '||id_calc||')
			) AS closest_pois )'
		);
		counter = counter + 1;
			
	END LOOP;
END 
$function$;
/*
--SELECT * FROM public.precalculate_grid(100, 100, 'grid_500'::TEXT, 15, ARRAY[[11.2570,48.1841]], 5, ARRAY[1], 1, 'walking_standard');
DROP TABLE IF EXISTS reached_pois_test;
CREATE TABLE reached_pois_test(cell_id int, object_id int, cost numeric, user_id int, scenario int, routing_method text, cost_sensitivity numeric, weighted_by_amenity numeric);
SELECT CalculateReachedPOIs(0, 'reached_pois_test', ARRAY[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20])
SELECT * FROM closest_reached_pois(0.0009, 300) AS closest_pois;


SELECT closest_pois.reached_cost AS cost, closest_pois.cell_id AS cell_id, closest_pois.object_id as object_id
			FROM (
				SELECT * FROM closest_reached_pois(0.0009, 2)
			) AS closest_pois

INSERT INTO userstest SELECT 111;
SELECT heatmap2(22)
*/