DROP FUNCTION IF EXISTS population_heatmap_geoserver;
CREATE OR REPLACE FUNCTION public.population_heatmap_geoserver(scenario_id_input integer, modus_input text DEFAULT 'default')
RETURNS TABLE(grid_id integer, population float, percentile_population integer, geom geometry)
LANGUAGE plpgsql
AS $function$
BEGIN 
	
	IF modus_input IN ('default', 'comparison') THEN 
		DROP TABLE IF EXISTS population_default;
		CREATE TEMP TABLE population_default AS 
		SELECT * FROM population_heatmap(scenario_id_input, 'default');
	END IF; 
	IF modus_input IN ('scenario','comparison') THEN 
		DROP TABLE IF EXISTS population_scenario;
		CREATE TEMP TABLE population_scenario AS 
		SELECT * FROM population_heatmap(scenario_id_input, 'scenario');
	END IF;
	IF modus_input IN ('comparison') THEN 
		ALTER TABLE population_default ADD PRIMARY KEY(grid_id); 
		ALTER TABLE population_scenario ADD PRIMARY KEY(grid_id); 
		DROP TABLE IF EXISTS population_comparison;
		
		CREATE TEMP TABLE population_comparison AS 
		WITH pop_difference AS 
		(
			SELECT d.grid_id, (COALESCE(s.population,0) - COALESCE(d.population,0)) AS population, d.geom
			FROM population_default d, population_scenario s
			WHERE d.grid_id = s.grid_id
		) 
		SELECT p.grid_id, p.population, 
		CASE 
		WHEN p.population = 0 THEN 0
		WHEN p.population < -400 THEN -5 
		WHEN p.population BETWEEN -400 AND -200 THEN -4 
		WHEN p.population BETWEEN -200 AND -80 THEN -3 
		WHEN p.population BETWEEN -80 AND -20 THEN -2 
		WHEN p.population BETWEEN -20 AND -1 THEN -1 
		WHEN p.population BETWEEN 1 AND 20 THEN 1 
		WHEN p.population BETWEEN 20 AND 80 THEN 2
		WHEN p.population BETWEEN 80 AND 200 THEN 3 
		WHEN p.population BETWEEN 200 AND 400 THEN 4 
		WHEN p.population  > 400 THEN 5 END AS percentile_population, p.geom 
		FROM pop_difference p;
	END IF; 
		
	IF modus_input = 'default' THEN 
		RETURN query 
		SELECT * FROM population_default;
	ELSEIF modus_input = 'scenario' THEN 
		RETURN query 
		SELECT * FROM population_scenario;
	ELSEIF modus_input = 'comparison' THEN 
		RETURN query 
		SELECT * FROM population_comparison;
	END IF; 

END
$function$;