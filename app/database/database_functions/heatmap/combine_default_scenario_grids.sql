DROP FUNCTION IF EXISTS combine_default_scenario_grids;
CREATE OR REPLACE FUNCTION combine_default_scenario_grids(gridids_default integer[], gridids_scenario integer[], arr_cost_default integer[],arr_cost_scenario integer[])
  RETURNS TABLE (gridids integer[], arr_cost integer[]) AS
$func$
	WITH d AS 
	(
		SELECT UNNEST(gridids_default) AS grid_id,
		UNNEST(arr_cost_default) AS true_cost
	), 
	s AS (
		SELECT UNNEST(gridids_scenario) AS grid_id,
		UNNEST(arr_cost_scenario) AS true_cost		
	), 
	u AS 
	(
		SELECT s.grid_id, s.true_cost 
		FROM d, s 
		WHERE d.grid_id = s.grid_id
		UNION ALL 
		SELECT d.* 
		FROM d
		LEFT JOIN s 
		ON d.grid_id = s.grid_id  
		WHERE s.grid_id IS NULL 
	)
	SELECT ARRAY_AGG(grid_id), array_agg(true_cost)
	FROM u;
$func$  LANGUAGE sql IMMUTABLE;