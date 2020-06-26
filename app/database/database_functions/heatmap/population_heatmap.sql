CREATE OR REPLACE FUNCTION public.population_heatmap(userid_input integer)
RETURNS TABLE(grid_id integer, population float, percentile_population integer, geom geometry)
LANGUAGE plpgsql
AS $function$
BEGIN 
	RETURN query
	WITH modified_population AS 
	(
		SELECT p.geom, -p.population AS population
		FROM population_userinput p 
		WHERE building_gid IN (SELECT UNNEST(deleted_feature_ids) FROM user_data WHERE layer_name = 'buildings' AND userid = userid_input)
		UNION ALL 
		SELECT p.geom, p.population 
		FROM population_userinput p 
		WHERE p.userid = userid_input
	),
	sum_pop AS (
		SELECT g.grid_id, sum(p.population) + COALESCE(g.population,0) population, 
		CASE WHEN sum(p.population) + COALESCE(g.population,0) BETWEEN 1 AND 20 THEN 1 
		WHEN sum(p.population) + COALESCE(g.population,0)  BETWEEN 20 AND 80 THEN 2
		WHEN sum(p.population) + COALESCE(g.population,0)  BETWEEN 80 AND 200 THEN 3 
		WHEN sum(p.population) + COALESCE(g.population,0)  BETWEEN 200 AND 400 THEN 4 
		WHEN sum(p.population) + COALESCE(g.population,0)  > 400 THEN 5 END AS percentile_population, g.geom
		FROM grid_500 g, modified_population p
		WHERE ST_Intersects(g.geom,p.geom)
		GROUP BY g.grid_id, g.population, g.geom
	) 
	SELECT * FROM sum_pop
	UNION ALL 
	SELECT g.grid_id, g.population, g.percentile_population, g.geom
	FROM grid_500 g
	LEFT JOIN sum_pop s
	ON g.grid_id = s.grid_id 
	WHERE s.grid_id IS NULL; 

END
$function$;