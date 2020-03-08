DROP FUNCTION IF EXISTS CalculateReachedPOIs;
CREATE OR REPLACE FUNCTION public.CalculateReachedPOIs(reached_pois_table text, ids_calc int[])
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
	EXECUTE format('CREATE TABLE '||reached_pois_table||'(cell_id int, object_id int, cost numeric, user_id int, scenario int, amenity text);');
		
	
	FOREACH id_calc IN ARRAY ids_calc
	LOOP 
		
		EXECUTE format('
			INSERT INTO '||reached_pois_table||' (SELECT closest_pois.cell_id AS cell_id, closest_pois.object_id as object_id, closest_pois.reached_cost AS cost, null, 0, closest_pois.amenity as amenity
			FROM (
				SELECT * FROM closest_reached_pois(0.0009, '||id_calc||')
			) AS closest_pois )'
		);
		counter = counter + 1;
			
	END LOOP;
END 
$function$;

/*
DROP TABLE reached_points_backup;
CREATE TABLE reached_points_backup AS SELECT * FROM reached_points;
DROP TABLE reached_points;
CREATE TABLE reached_points AS SELECT * FROM reached_pois_test;



WITH grid_ids AS (
	SELECT array_agg(grid_id) AS ids FROM grid_500
)
SELECT CalculateReachedPOIs('reached_pois_test', ids) FROM grid_ids
       


*/