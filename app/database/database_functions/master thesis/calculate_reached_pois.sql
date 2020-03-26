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
	
	FOREACH id_calc IN ARRAY ids_calc
	LOOP 
		
		EXECUTE format('
			INSERT INTO '||reached_pois_table||' (SELECT closest_pois.cell_id AS cell_id, closest_pois.object_id as object_id, closest_pois.reached_cost AS cost, closest_pois.amenity as amenity, NULL, 0
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


DELETE FROM reached_points;
WITH grid_ids AS (
	SELECT array_agg(grid_id) AS ids FROM grid_500 WHERE grid_id >= 100
)
SELECT CalculateReachedPOIs('reached_points', ids) FROM grid_ids
       


*/