CREATE OR REPLACE FUNCTION basic.reachable_population_study_area(scenario_id_input integer, modus text, study_area_ids integer[])
 RETURNS TABLE(sub_study_area_id integer, name TEXT, population integer)
 LANGUAGE plpgsql
AS $function$ 
DECLARE 	
	excluded_buildings_id integer[] := '{}'::integer[];
BEGIN
	
	DROP TABLE IF EXISTS reachable_population; 

	/*Get reachable population*/
	IF modus = 'default' THEN
		RETURN query
		SELECT s.id AS sub_study_area_id, s.name, s.population 
		FROM basic.sub_study_area s
		WHERE s.id IN (SELECT UNNEST(study_area_ids)); 
	
	ELSEIF modus = 'scenario' THEN 
		excluded_buildings_id  = basic.modified_buildings(scenario_id_input);
		
		RETURN query 
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
		 	SELECT p.sub_study_area_id, sum(p.population) population 
		 	FROM prepared_scenario p 
		 	GROUP BY p.sub_study_area_id
		)
		SELECT s.id AS sub_study_area_id, s.name, (s.population + COALESCE(sp.population, 0))::integer AS population 
		FROM basic.sub_study_area s
		LEFT JOIN scenario_population sp 
		ON s.id = sp.sub_study_area_id
		WHERE s.id IN (SELECT UNNEST(study_area_ids)); 	

	ELSE 
		RAISE EXCEPTION 'Unknown modus: %', modus;	
	END IF;
	
 
END; 
$function$;

/*
SELECT * 
FROM basic.reachable_population_study_area(2,'default', ARRAY[17,24,26])
*/