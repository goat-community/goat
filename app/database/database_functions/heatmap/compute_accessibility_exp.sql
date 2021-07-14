DROP FUNCTION IF EXISTS compute_accessibility_exp;
CREATE OR REPLACE FUNCTION compute_accessibility_exp(scenario_id_input integer)
  /*RETURNS SETOF gid,  AS*/
	returns table (grid_id integer, accessibility_indices bigint)
as $func$

BEGIN
	DROP TABLE IF EXISTS computed_accessibility; 
	CREATE TEMP TABLE computed_accessibility AS  
	WITH x AS 
	(
		SELECT gid, ((arr_cost)::real[] @* -s.sensitivity::real) AS pre_accessibility
		FROM reached_pois_heatmap rph, (SELECT UNNEST(select_from_variable_container('heatmap_sensitivities_exp'))  sensitivity) s 
		WHERE scenario_id = scenario_id_input
	)
	SELECT gid, array_agg(vec_pow(exp(1.0)::real,pre_accessibility) @* 10000::REAL)::integer[] AS accessibility_indices_exp
	FROM x
	GROUP BY gid; 
	
	ALTER TABLE computed_accessibility ADD PRIMARY key(gid);
	
	UPDATE reached_pois_heatmap r SET accessibility_indices_exp = t.accessibility_indices_exp 
	FROM computed_accessibility t 
	WHERE r.gid = t.gid
	AND r.scenario_id = scenario_id_input;
END;

$func$  LANGUAGE plpgsql;
