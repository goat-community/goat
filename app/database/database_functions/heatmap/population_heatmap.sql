CREATE OR REPLACE FUNCTION public.population_heatmap(scenario_id_input integer, modus_input text DEFAULT 'default')
RETURNS TABLE(grid_id integer, population float, percentile_population integer, geom geometry)
LANGUAGE plpgsql
AS $function$
BEGIN 
	
	IF modus_input = 'default' THEN 
		scenario_id_input = 0;
	END IF;
	
	RETURN query
	WITH modified_population AS 
	(
		SELECT p.geom, -p.population AS population
		FROM population_userinput p 
		WHERE building_gid IN (SELECT UNNEST(deleted_buildings) FROM scenarios WHERE scenario_id = scenario_id_input)
		UNION ALL 
		SELECT p.geom, p.population 
		FROM population_userinput p 
		WHERE p.scenario_id = scenario_id_input
	),
	sum_pop AS (
		SELECT g.grid_id, sum(p.population) + COALESCE(g.population,0) population, 
		CASE WHEN sum(p.population) + COALESCE(g.population,0) BETWEEN 1 AND 20 THEN 1 
		WHEN sum(p.population) + COALESCE(g.population,0)  BETWEEN 20 AND 80 THEN 2
		WHEN sum(p.population) + COALESCE(g.population,0)  BETWEEN 80 AND 200 THEN 3 
		WHEN sum(p.population) + COALESCE(g.population,0)  BETWEEN 200 AND 400 THEN 4 
		WHEN sum(p.population) + COALESCE(g.population,0)  > 400 THEN 5 END AS percentile_population, g.geom
		FROM grid_heatmap g, modified_population p
		WHERE ST_Intersects(g.geom,p.geom)
		GROUP BY g.grid_id, g.population, g.geom
	) 
	SELECT s.grid_id, s.population::float, s.percentile_population, s.geom 
	FROM sum_pop s
	UNION ALL 
	SELECT g.grid_id, g.population, g.percentile_population, g.geom
	FROM grid_heatmap g
	LEFT JOIN sum_pop s
	ON g.grid_id = s.grid_id 
	WHERE s.grid_id IS NULL; 

END
$function$;