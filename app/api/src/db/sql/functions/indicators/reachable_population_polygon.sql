CREATE OR REPLACE FUNCTION basic.reachable_population_polygon(scenario_id_input integer, modus TEXT, region TEXT) 
RETURNS TABLE (name TEXT, population integer)
AS $function$ 
DECLARE 	
	excluded_buildings_id integer[];
	region_geom geometry := ST_SETSRID(ST_GeomFromText(region), 4326);
	reachable_population integer; 
	reachable_population_default integer; 
	reachable_population_scenario integer;  
BEGIN
	
	/*Check if invalid modus*/
	IF modus NOT IN ('default','scenario') THEN 
		RAISE EXCEPTION 'Unknown modus: %', modus;	
	END IF;
	/*Get reachable population*/
	IF modus IN ('default','scenario')  THEN
		WITH pop AS 
		(
			SELECT COALESCE(SUM(p.population), 0) population 
			FROM basic.population p 
			WHERE ST_Intersects(p.geom, region_geom)
		)
		SELECT p.population 
		INTO reachable_population_default
		FROM pop p;
		
	END IF; 
	
	IF modus = 'default' THEN 
		reachable_population = reachable_population_default::integer;
	END IF; 

	IF modus = 'scenario' THEN 
		excluded_buildings_id  = basic.modified_buildings(scenario_id_input);
		
		WITH prepared_scenario AS 
		(
			SELECT COALESCE(-sum(p.population), 0) AS population 
			FROM basic.population p 
			WHERE ST_Intersects(p.geom, region_geom)
			AND p.building_id IN (SELECT UNNEST(excluded_buildings_id))	
			UNION ALL 
			SELECT COALESCE(sum(p.population), 0) AS population
		 	FROM customer.population_modified p 
		 	WHERE ST_Intersects(p.geom, region_geom)
		 	AND p.scenario_id = scenario_id_input
	 	)
 		SELECT COALESCE(sum(p.population), 0)::integer 
 		INTO reachable_population_scenario  
		FROM prepared_scenario p; 
		reachable_population = (reachable_population_default  + reachable_population_scenario)::integer;
	END IF; 


	RETURN query 
	SELECT 'polygon' AS name, floor((reachable_population / 5)*5)::integer AS population; 

END; 
$function$ LANGUAGE plpgsql;

/*
SELECT * 
FROM basic.reachable_population_polygon(2, 'default',
'POLYGON ((11.570115749093093 48.15360025891228, 11.570274296106232 48.1518693270582, 11.572708788648153 48.15118483030911, 11.574984827528402 48.15223125586774, 11.574826384986741 48.15396220424526, 11.57239179909107 48.154646710542, 11.570115749093093 48.15360025891228))') 
*/
