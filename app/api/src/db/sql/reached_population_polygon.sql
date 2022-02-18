CREATE OR REPLACE FUNCTION basic.reached_population_polygon(ischrone_calculation_id_input integer, scenario_id_input integer, modus TEXT, region TEXT) 
RETURNS TABLE (isochrone_feature_id integer, reached_opportunities jsonb)
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
		SELECT COALESCE(population, 0)  
		INTO reachable_population_default
		FROM basic.population p 
		WHERE ST_Intersects(p.geom, region_geom); 
	END IF; 
	
	IF modus = 'scenario' THEN 
		excluded_buildings_id  = (SELECT s.deleted_buildings FROM customer.scenario s WHERE id = scenario_id_input);
		
		WITH prepared_scenario AS 
		(
			SELECT -sum(p.population) AS population 
			FROM basic.population p 
			WHERE ST_Intersects(p.geom, region_geom)
			AND p.building_id IN (SELECT UNNEST(excluded_buildings_id))	
			UNION ALL 
			SELECT sum(p.population) AS population
		 	FROM customer.population_modified p 
		 	WHERE ST_Intersects(p.geom, region_geom)
		 	AND p.scenario_id = scenario_id_input
	 	)
 		SELECT COALESCE(sum(population), 0)::integer 
 		INTO reachable_population_scenario  
		FROM prepared_scenario p; 
	
		reachable_population = floor((reachable_population_default  + reachable_population_scenario / 5)*5); 
		
	END IF; 
	
	reachable_population = floor((reachable_population_default / 5)*5);

	/*Get reached population*/
	DROP TABLE IF EXISTS reached_population; 
	CREATE TEMP TABLE reached_population AS 
	WITH to_group AS 
	(
		SELECT i.id, s.population
		FROM customer.isochrone_feature i
		CROSS JOIN LATERAL 
		(
		 	SELECT sum(p.population) AS population
		 	FROM basic.population p 
		 	WHERE st_intersects(i.geom,p.geom)
		 	AND st_intersects(p.geom, region_geom)
		 	AND p.building_id NOT IN (SELECT UNNEST(excluded_buildings_id))	
		) s
		WHERE i.isochrone_calculation_id = ischrone_calculation_id_input
		UNION ALL 
		SELECT i.id, s.population
		FROM customer.isochrone_feature i
		CROSS JOIN LATERAL 
		(
		 	SELECT sum(p.population) AS population
		 	FROM customer.population_modified p 
		 	WHERE st_intersects(i.geom,p.geom)
		 	AND st_intersects(p.geom, region_geom)
		 	AND p.scenario_id = scenario_id_input
		) s
		WHERE i.isochrone_calculation_id = ischrone_calculation_id_input
	)
	SELECT g.id AS isochrone_feature_id,(floor(COALESCE(sum(g.population)::integer,0)/5)*5) AS population
	FROM to_group g
	GROUP BY g.id;
	
    /*Combine and return results*/
	RETURN query 
	UPDATE customer.isochrone_feature i
	SET reached_opportunities = jsonb_build_object('name', 'polygon', 'reached_population', population, 'total_population', reachable_population)  
	FROM reached_population r 
	WHERE i.id = r.isochrone_feature_id
	RETURNING i.id, i.reached_opportunities;

END; 
$function$ LANGUAGE plpgsql;

/*
SELECT * 
FROM basic.reached_population_polygon(88, 2, 'default',
'POLYGON ((11.570115749093093 48.15360025891228, 11.570274296106232 48.1518693270582, 11.572708788648153 48.15118483030911, 11.574984827528402 48.15223125586774, 11.574826384986741 48.15396220424526, 11.57239179909107 48.154646710542, 11.570115749093093 48.15360025891228))') 
*/