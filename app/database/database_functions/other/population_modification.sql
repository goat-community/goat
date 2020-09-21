DROP FUNCTION IF EXISTS population_modification;
CREATE OR REPLACE FUNCTION public.population_modification(userid_input integer)
RETURNS SETOF void
LANGUAGE plpgsql
AS $function$
DECLARE 
	average_gross_living_area integer := select_from_variable_container_s('average_gross_living_area');
BEGIN 
	DELETE FROM population_userinput WHERE userid = userid_input;

	INSERT INTO population_userinput (geom, population, building_gid, userid)
	WITH count_pop AS (
		SELECT count(*) AS count_points, building_gid
		FROM population_modified 
		WHERE userid = userid_input
		GROUP BY building_gid 
	)
	SELECT p.geom,
	CASE WHEN b.population IS NULL THEN (b.building_levels_residential * ST_AREA(b.geom::geography)/average_gross_living_area)/c.count_points ELSE b.population/c.count_points END AS population, 
	b.gid, userid_input
	FROM buildings_modified b, population_modified p, count_pop c  
	WHERE b.original_id IS NULL 
	AND b.gid = p.building_gid 
	AND b.gid = c.building_gid
	AND b.userid = userid_input
	AND p.userid = userid_input
	AND b.building = 'residential';

	WITH to_update AS 
	(
		SELECT building_gid, sum(population) population
		FROM population_userinput 
		WHERE userid = userid_input
		GROUP BY gid 
	)
	UPDATE buildings_modified 
	SET population = u.population 
	FROM to_update u 
	WHERE gid = u.building_gid
	AND userid = userid_input; 

END
$function$;
