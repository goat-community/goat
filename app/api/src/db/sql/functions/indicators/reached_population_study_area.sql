CREATE OR REPLACE FUNCTION basic.reached_population_study_area(ischrone_calculation_id_input integer, scenario_id_input integer, modus text, study_area_ids integer[])
 RETURNS TABLE(id integer, step integer, reached_opportunities jsonb)
 LANGUAGE plpgsql
AS $function$ 
DECLARE 	
	excluded_buildings_id integer[] := '{}'::integer[];
BEGIN
	
	DROP TABLE IF EXISTS reachable_population; 

	/*Get reachable population*/
	IF modus = 'default' THEN
		CREATE TEMP TABLE reachable_population AS 
		SELECT i.id AS isochrone_feature_id, s.id AS sub_study_area_id, s.name, s.population 
		FROM basic.sub_study_area s, customer.isochrone_feature i 
		WHERE s.id IN (SELECT UNNEST(study_area_ids))
		AND i.isochrone_calculation_id = ischrone_calculation_id_input; 
	
	ELSEIF modus = 'scenario' THEN 
		excluded_buildings_id  = basic.modified_buildings(scenario_id_input);
		
		CREATE TEMP TABLE reachable_population AS 
		WITH prepared_scenario AS 
		(
			SELECT p.sub_study_area_id, -sum(p.population) AS population 
			FROM basic.population p 
			WHERE p.sub_study_area_id IN (SELECT UNNEST(study_area_ids))
			AND p.building_id IN (SELECT UNNEST(excluded_buildings_id))	
			GROUP BY p.sub_study_area_id 
			UNION ALL 
			SELECT p.sub_study_area_id, sum(p.population) AS population
		 	FROM customer.population_modified p 
		 	WHERE p.sub_study_area_id IN (SELECT UNNEST(study_area_ids))
		 	AND p.scenario_id = scenario_id_input
		 	GROUP BY p.sub_study_area_id 
	 	),
	 	scenario_population AS 
	 	(
		 	SELECT p.sub_study_area_id, sum(population) population 
		 	FROM prepared_scenario p 
		 	GROUP BY p.sub_study_area_id
		),
		combined_population AS 
		( 
			SELECT s.id AS sub_study_area_id, s.name, (s.population + COALESCE(sp.population, 0)) AS population 
			FROM basic.sub_study_area s
			LEFT JOIN scenario_population sp 
			ON s.id = sp.sub_study_area_id
			WHERE s.id IN (SELECT UNNEST(study_area_ids)) 	
		)
		SELECT i.id AS isochrone_feature_id, c.*
		FROM customer.isochrone_feature i, combined_population c
		WHERE i.isochrone_calculation_id = ischrone_calculation_id_input; 
	ELSE 
		RAISE EXCEPTION 'Unknown modus: %', modus;	
	END IF;
	
	/*Get reached population*/
	DROP TABLE IF EXISTS reached_population; 
	CREATE TEMP TABLE reached_population AS 
	WITH to_group AS 
	(
		SELECT i.id, s.population, s.sub_study_area_id
		FROM customer.isochrone_feature i
		CROSS JOIN LATERAL 
		(
		 	SELECT p.sub_study_area_id, sum(p.population) AS population
		 	FROM basic.population p 
		 	WHERE st_intersects(i.geom,p.geom)
		 	AND p.building_id NOT IN (SELECT UNNEST(excluded_buildings_id))	
		 	AND p.sub_study_area_id IN (SELECT UNNEST(study_area_ids))
		 	GROUP BY p.sub_study_area_id 
		) s
		WHERE i.isochrone_calculation_id = ischrone_calculation_id_input
		UNION ALL 
		SELECT i.id, s.population, s.sub_study_area_id
		FROM customer.isochrone_feature i
		CROSS JOIN LATERAL 
		(
		 	SELECT p.sub_study_area_id, sum(p.population) AS population
		 	FROM customer.population_modified p 
		 	WHERE st_intersects(i.geom,p.geom)
		 	AND p.sub_study_area_id IN (SELECT UNNEST(study_area_ids))
		 	AND p.scenario_id = scenario_id_input
		 	GROUP BY p.sub_study_area_id 
		) s
		WHERE i.isochrone_calculation_id = ischrone_calculation_id_input 
	)
	SELECT g.id, (floor(COALESCE(sum(g.population)::integer,0)/5)*5) AS population, g.sub_study_area_id 
	FROM to_group g
	GROUP BY g.id, g.sub_study_area_id; 
	
	/*Combine and return results*/
	RETURN query 
	WITH combined AS 
	(
		SELECT a.isochrone_feature_id, a.sub_study_area_id, a.name, 
		CASE WHEN COALESCE(r.population, 0) > a.population THEN a.population 
		ELSE COALESCE(r.population, 0) END AS reached_population, a.population AS total_population 
		FROM reachable_population a
		LEFT JOIN reached_population r 
		ON a.isochrone_feature_id = r.id 
		AND a.sub_study_area_id = r.sub_study_area_id
	),
	as_object AS 
	(
		SELECT c.isochrone_feature_id, jsonb_object_agg(c.sub_study_area_id, 
		jsonb_build_object('name', c.name, 'reached_population', c.reached_population::integer, 'total_population', c.total_population::integer)) AS population 
		FROM combined c
		GROUP BY c.isochrone_feature_id 
	)
	UPDATE customer.isochrone_feature i
	SET reached_opportunities = o.population 
	FROM as_object o 
	WHERE o.isochrone_feature_id = i.id
	RETURNING i.id, i.step, i.reached_opportunities;
 
END; 
$function$;

/*
SELECT * 
FROM basic.reached_population_study_area(39, 2,'default', ARRAY[17,24,26])
*/
