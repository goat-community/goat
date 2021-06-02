DROP FUNCTION IF EXISTS compute_accessibility_population;
CREATE OR REPLACE FUNCTION compute_accessibility_population(scenario_id_input integer)
  RETURNS SETOF void AS
$func$
'''Problem with pre_accessibility --> s.sensitivity=0 (for CUM) will result in Division by zero and thus abbortion of the calculation'''
BEGIN
	DROP TABLE IF EXISTS computed_accessibility; 
	CREATE TEMP TABLE computed_accessibility AS  
	WITH x AS 
	(
		SELECT pop_gid, population, unnest(gids) as gid, ((arr_cost @* arr_cost)::real[] @/ -s.sensitivity::real) AS pre_accessibility
		FROM reached_population_pois rph, (SELECT UNNEST(select_from_variable_container('heatmap_sensitivities'))  sensitivity) s 
		WHERE scenario_id = scenario_id_input
	)
	SELECT pop_gid, array_agg(vec_pow(exp(1.0)::real,pre_accessibility) @* 10000::REAL)::integer[] AS accessibility_indices
	FROM x
	GROUP BY pop_gid; 
	
	ALTER TABLE computed_accessibility ADD PRIMARY key(pop_gid);
	
	UPDATE reached_population_pois r SET accessibility_indices = t.accessibility_indices 
	FROM computed_accessibility t 
	WHERE r.pop_gid = t.pop_gid
	AND r.scenario_id = scenario_id_input;

	DROP TABLE IF EXISTS computed_accessibility_pop; 
	CREATE TEMP TABLE computed_accessibility_pop AS  
	WITH x AS 
	(
		SELECT u.pop_id, u.accessibility_index * (x.population)::SMALLINT AS accessibility_index, x.population 
		FROM (
			SELECT pop_id, accessibility_index, population
			FROM reached_full_edges 
			)x, UNNEST(x.gridids, x.accessibility_index) AS u(grid_id, accessibility_index)) s group by s.grid_id);"""

END;
$func$  LANGUAGE plpgsql;

/*SELECT compute_accessibility(0)*/

/*compute cumulative opportunities*/
/*BEGIN
	DROP TABLE IF EXISTS computed_cum; 
	CREATE TEMP TABLE computed_cum AS  
	WITH x AS 
	(
		SELECT gid, 0 AS pre_cum
		FROM reached_pois_heatmap rph, (SELECT UNNEST(select_from_variable_container('heatmap_sensitivities'))  sensitivity) s 
		WHERE scenario_id = scenario_id_input
	)
	SELECT gid, array_agg(vec_pow(exp(1.0)::real,pre_cum) @* 10000::REAL)::integer[] AS cum_indices 
	FROM x
	GROUP BY gid; 
	
	ALTER TABLE computed_cum ADD PRIMARY key(gid);
	
	UPDATE reached_pois_heatmap r SET cum_indices = t.cum_indices 
	FROM computed_cum t 
	WHERE r.gid = t.gid
	AND r.scenario_id = scenario_id_input;
END;

$func$  LANGUAGE plpgsql;*/