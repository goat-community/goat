DROP FUNCTION IF EXISTS heatmap_population_api;
CREATE OR REPLACE FUNCTION public.heatmap_population_api(modus_input text, scenario_id_input integer)
RETURNS TABLE(grid_id integer, population float, percentile_population integer, modus text, geom geometry)
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
		SELECT p.grid_id, p.population, p.percentile_population, modus_input AS modus, p.geom FROM population_default p;
	ELSEIF modus_input = 'scenario' THEN 
		RETURN query 
		SELECT p.grid_id, p.population, p.percentile_population, modus_input AS modus, p.geom FROM population_scenario p;
	ELSEIF modus_input = 'comparison' THEN 
		RETURN query 
		SELECT p.grid_id, p.population, p.percentile_population, modus_input AS modus, p.geom FROM population_comparison p;
	END IF; 

END
$function$;

/*SELECT heatmap_population_api('default',1)*/