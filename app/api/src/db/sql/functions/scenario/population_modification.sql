CREATE OR REPLACE FUNCTION basic.population_modification(scenario_id_input integer)
RETURNS SETOF void
LANGUAGE plpgsql
AS $function$
DECLARE 
	average_gross_living_area integer := basic.select_customization('average_gross_living_area');
BEGIN 

	UPDATE customer.building_modified b
	SET area = ST_AREA(geom::geography), population = (b.building_levels_residential * ST_AREA(b.geom::geography) / average_gross_living_area) 
	WHERE scenario_id = scenario_id_input; 
	
	WITH count_pop AS (
		SELECT count(*) AS count_points, building_modified_id 
		FROM customer.population_modified 
		WHERE scenario_id = scenario_id_input
		GROUP BY building_modified_id  
	),
	points_to_update AS 
	(
		SELECT p.id, b.id AS building_modified_id, b.population / c.count_points AS population 
		FROM customer.building_modified b, customer.population_modified p, count_pop c  
		WHERE b.id = p.building_modified_id  
		AND b.id = c.building_modified_id  
		AND b.scenario_id = scenario_id_input
		AND p.scenario_id = scenario_id_input
		AND b.building_type = 'residential'
	)
	UPDATE customer.population_modified p 
	SET population = u.population 
	FROM points_to_update u 
	WHERE p.id = u.id; 

END
$function$;
/*
SELECT basic.population_modification(13)
*/