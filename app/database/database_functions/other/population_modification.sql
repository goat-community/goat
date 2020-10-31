DROP FUNCTION IF EXISTS population_modification;
CREATE OR REPLACE FUNCTION public.population_modification(scenario_id_input integer)
RETURNS SETOF void
LANGUAGE plpgsql
AS $function$
DECLARE 
	average_gross_living_area integer := select_from_variable_container_s('average_gross_living_area');
BEGIN 
	DELETE FROM population_userinput WHERE scenario_id = scenario_id_input;

	INSERT INTO population_userinput (geom, population, building_gid, scenario_id)
	WITH count_pop AS (
		SELECT count(*) AS count_points, building_gid
		FROM population_modified 
		WHERE scenario_id = scenario_id_input
		GROUP BY building_gid 
	)
	SELECT p.geom,
	CASE WHEN b.population IS NULL THEN (b.building_levels_residential * ST_AREA(b.geom::geography)/average_gross_living_area)/c.count_points ELSE b.population/c.count_points END AS population, 
	b.gid, scenario_id_input
	FROM buildings_modified b, population_modified p, count_pop c  
	WHERE b.original_id IS NULL 
	AND b.gid = p.building_gid 
	AND b.gid = c.building_gid
	AND b.scenario_id = scenario_id_input
	AND p.scenario_id = scenario_id_input
	AND b.building = 'residential';

	WITH to_update AS 
	(
		SELECT building_gid, sum(population) population
		FROM population_userinput 
		WHERE scenario_id = scenario_id_input
		GROUP BY building_gid
	)
	UPDATE buildings_modified 
	SET population = u.population 
	FROM to_update u 
	WHERE gid = u.building_gid
	AND scenario_id = scenario_id_input; 

END
$function$;