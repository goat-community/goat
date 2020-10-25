------------------------------------------------------------------------------------------
----------------------------Goat Classified population in grid----------------------------
------------------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION assign_population_categories (input_table TEXT, input_column TEXT, output_table TEXT, output_column TEXT, base_grid text)
RETURNS void
LANGUAGE plpgsql
AS $function$
BEGIN
	DROP TABLE IF EXISTS grouped_array;
	CREATE TABLE grouped_array (grid_id int4, pop_groups integer[]);
	
	EXECUTE '
	INSERT INTO grouped_array(
	SELECT grid_id, p.'|| quote_ident(input_column) ||' FROM '||quote_ident(base_grid)||' g
	JOIN '|| quote_ident(input_table) ||' p   
	ON ST_Intersects(g.geom, st_centroid(p.geom)))';

	DROP TABLE IF EXISTS population_array_per_hexagon;
	CREATE TABLE population_array_per_hexagon (LIKE grouped_array INCLUDING all);

	EXECUTE 'INSERT INTO population_array_per_hexagon (
	select grid_id, array_agg(elem order by ordinality) AS outputs 
	from (
	   	select grid_id, ordinality, sum(elem) as elem
    	from grouped_array
    	cross join unnest(pop_groups) with ordinality as u(elem, ordinality)
    	group by 1, 2
    	) s
	group by 1
	order by 1)';
	
-- New grid with categorized pop
	EXECUTE 'DROP TABLE IF EXISTS '||quote_ident(output_table);
	EXECUTE ' CREATE TABLE '||quote_ident(output_table)||'(LIKE '||quote_ident(base_grid)||' INCLUDING ALL)';
	EXECUTE 'ALTER TABLE '||quote_ident(output_table)||'
	add '||quote_ident(output_column)||' integer[]';
	
	EXECUTE 'INSERT INTO '||quote_ident(output_table)||'(
	SELECT g.*, p.pop_groups AS pop_array FROM '||quote_ident(base_grid)||' g
	LEFT JOIN population_array_per_hexagon p
	ON g.grid_id = p.grid_id)';

END;
$function$;

-- Population_array_per_hexagon
-- DESCRIPTION:				Takes one array_column from the input table, and aggregates values inside the array by each hexagon (or unit defined in the base_grid)
-- INPUT PARAMETERS:
-- input_table (text) 		Select the table with the array column that contains the population categories.
-- input_column (text)		Name of the array column in (input_table) to be used in the join.
-- output_table (text)		Name of the new output table
-- output_column (text)		Name for the new array column in the output_table
-- base_grid (text)			Grid to use as base, the output table will have this structure + a new array column

-- Examples:

-- 1 round
-- SELECT assign_population_categories('population_classificated_array', 'pop_age_groups', 'grid_500_age', 'array_ages','grid_heatmap');

-- 2 round
-- SELECT assign_population_categories('population_classificated_array', 'pop_gender_array', 'grid_500_age_gender', 'array_gender','grid_500_age');

