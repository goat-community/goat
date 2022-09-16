CREATE OR REPLACE FUNCTION basic.get_population_sum(user_id_input integer, modus text, extent geometry, pixel_resolution integer, scenario_id_input integer DEFAULT 0)
 RETURNS TABLE(pixel int[], population float)
 LANGUAGE plpgsql
AS $function$
DECLARE 
	excluded_buildings_id integer[] := ARRAY[]::integer[];
BEGIN 		

	IF modus = 'scenario' THEN
		excluded_buildings_id  = basic.modified_buildings(scenario_id_input);
	ELSE 
		scenario_id_input = 0;
	END IF;

	RETURN query
	SELECT x.pixel, sum(x.population) AS population 
	FROM 
	(
	 	SELECT basic.coordinate_to_pixel(ST_Y(geom), ST_X(geom), pixel_resolution) AS pixel, p.population AS population
	 	FROM basic.population p 
	 	WHERE st_intersects(p.geom, extent)
	 	AND p.building_id NOT IN (SELECT UNNEST(excluded_buildings_id))
		UNION ALL 		
	    SELECT basic.coordinate_to_pixel(ST_Y(geom), ST_X(geom), pixel_resolution) AS pixel, p.population AS population
	 	FROM customer.population_modified p 
	 	WHERE st_intersects(p.geom, extent)
	 	AND p.scenario_id = scenario_id_input 
 	) x
 	GROUP BY x.pixel; 
 	
END ;
$function$;

/*SELECT *
FROM basic.get_population_sum(15, 'default'::text, ST_SETSRID(ST_BUFFER(ST_MAKEPOINT(11.57616,48.13168)::geography, 200000)::geometry, 4326), 10) 
*/