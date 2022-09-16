CREATE OR REPLACE FUNCTION basic.prepare_heatmap_population(active_study_area_id integer, modus_input text DEFAULT 'default'::text, scenario_id_input integer DEFAULT 0)
 RETURNS TABLE(grid_visualization_id bigint, population double precision, percentile_population integer, geom geometry)
 LANGUAGE plpgsql
AS $function$
DECLARE 
	modified_buildings integer[];
BEGIN 

	IF modus_input = 'default' THEN 
		scenario_id_input = 0;
	END IF;

	modified_buildings = basic.modified_buildings(scenario_id_input);
	RETURN query
	WITH modified_population AS 
	(
		SELECT p.geom, -p.population AS population
		FROM basic.population p 
		WHERE building_id IN (SELECT UNNEST(modified_buildings))
		UNION ALL 
		SELECT p.geom, p.population 
		FROM customer.population_modified p 
		WHERE p.scenario_id = scenario_id_input 
	),
	sum_pop AS (
		SELECT g.id, sum(p.population) + COALESCE(g.population,0) population, 
		CASE WHEN sum(p.population) + COALESCE(g.population,0) BETWEEN 1 AND 80 THEN 1 
		WHEN sum(p.population) + COALESCE(g.population,0)  BETWEEN 80 AND 200 THEN 2
		WHEN sum(p.population) + COALESCE(g.population,0)  BETWEEN 200 AND 500 THEN 3 
		WHEN sum(p.population) + COALESCE(g.population,0)  BETWEEN 500 AND 1000 THEN 4 
		WHEN sum(p.population) + COALESCE(g.population,0)  > 1000 THEN 5 END AS percentile_population, g.geom
		FROM basic.grid_visualization g, modified_population p, basic.study_area_grid_visualization s
		WHERE ST_Intersects(g.geom,p.geom)
		AND p.population IS NOT NULL 
		AND g.id = s.grid_visualization_id 
		AND s.study_area_id = active_study_area_id
		GROUP BY g.id, g.population, g.geom
	) 
	SELECT s.id AS grid_visualization_id ,s.population, s.percentile_population, s.geom 
	FROM sum_pop s
	UNION ALL 
	SELECT g.id AS grid_visualization_id, g.population, g.percentile_population, g.geom
	FROM 
	(
		SELECT g.* 
		FROM basic.grid_visualization  g, basic.study_area_grid_visualization sa
		WHERE sa.study_area_id = active_study_area_id 
		AND g.id = sa.grid_visualization_id 
	) g 
	LEFT JOIN sum_pop s
	ON g.id = s.id
	WHERE s.id IS NULL;
	
END
$function$;
/*
SELECT * 
FROM basic.prepare_heatmap_population(13)
*/