CREATE OR REPLACE FUNCTION basic.get_population_multi_sum(user_id_input integer, modus text, extent geometry, sub_study_area_ids integer[], pixel_resolution integer, scenario_id_input integer DEFAULT 0)
 RETURNS TABLE(pixel integer[], population double precision, sub_study_area_id integer)
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
	SELECT x.pixel, sum(x.population) AS population, x.sub_study_area_id  
	FROM 
	(
	 	SELECT basic.coordinate_to_pixel(ST_Y(geom), ST_X(geom), pixel_resolution) AS pixel, p.population AS population, p.sub_study_area_id
	 	FROM basic.population p 
	 	WHERE st_intersects(p.geom, extent)
	 	AND p.building_id NOT IN (SELECT UNNEST(excluded_buildings_id))
	 	AND p.sub_study_area_id IN (SELECT UNNEST(sub_study_area_ids))
		UNION ALL 		
	    SELECT basic.coordinate_to_pixel(ST_Y(geom), ST_X(geom), pixel_resolution) AS pixel, p.population AS population, p.sub_study_area_id
	 	FROM customer.population_modified p 
	 	WHERE st_intersects(p.geom, extent)
	 	AND p.scenario_id = scenario_id_input 
	 	AND p.sub_study_area_id IN (SELECT UNNEST(sub_study_area_ids))
 	) x
 	GROUP BY x.pixel, x.sub_study_area_id; 
 	
END ;
$function$;

/*
SELECT * 
FROM basic.get_population_multi_sum(
15, 'default'::text, ST_SETSRID(ST_BUFFER(ST_MAKEPOINT(11.57616,48.13168)::geography, 200000)::geometry, 4326), ARRAY[1,2,3,4,5], 3) 
*/