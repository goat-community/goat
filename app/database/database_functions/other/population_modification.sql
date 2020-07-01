DROP FUNCTION IF EXISTS population_modification;
CREATE OR REPLACE FUNCTION public.population_modification(userid_input integer)
RETURNS SETOF void
LANGUAGE plpgsql
AS $function$
DECLARE 
	average_gross_living_area integer := select_from_variable_container_s('average_gross_living_area');
BEGIN 
	DELETE FROM population_userinput WHERE userid = userid_input;

	INSERT INTO population_userinput (building_levels, building_levels_residential, area, geom, population, building_gid, userid)
	WITH count_pop AS (
		SELECT count(*) AS count_points, building_gid
		FROM population_modified 
		WHERE userid = userid_input
		GROUP BY building_gid 
	)
	SELECT b.building_levels, building_levels_residential, ST_AREA(b.geom::geography)::integer, p.geom,
	CASE WHEN b.population IS NULL THEN (b.building_levels_residential * ST_AREA(b.geom::geography)/average_gross_living_area)/c.count_points ELSE b.population/c.count_points END AS population, 
	b.gid, userid_input
	FROM buildings_modified b, population_modified p, count_pop c  
	WHERE b.original_id IS NULL 
	AND b.gid = p.building_gid 
	AND b.gid = c.building_gid
	AND b.userid = userid_input
	AND p.userid = userid_input
	AND b.building = 'residential';
END
$function$;

