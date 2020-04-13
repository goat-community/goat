DROP FUNCTION IF EXISTS precalculate_grid;
CREATE OR REPLACE FUNCTION public.precalculate_grid(userid_input integer, grid text, minutes integer,points_array NUMERIC[][],speed_input NUMERIC, ids_calc int[], modus_input integer,routing_profile_input text)
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
		INSERT INTO isochrones(geom,step,objectid) 
        SELECT geom, step, id_calc 
        FROM isochrones_alphashape(userid_input,minutes,points_array[counter][1],points_array[counter][2], 
        number_isochrones, speed_input, alphashape_parameter_input, modus_input, id_calc, 1, routing_profile_input);

/*		
		EXECUTE format('
			UPDATE '||grid||' set pois = closest_pois, area_isochrone = x.area
			FROM (
				SELECT ST_Area(geom) as area, closest_pois(0.0009,objectid)
				FROM isochrones i
				WHERE objectid ='||id_calc||'
			) x
			WHERE grid_id = '||id_calc
		);
*/
		counter = counter + 1;
			
	END LOOP;
END 
$function$;

--SELECT * FROM public.precalculate_grid(100, 100, 'grid_500'::TEXT, 15, ARRAY[[11.2570,48.1841]], 5, ARRAY[1], 1, 'walking_standard');


