------------------------------------------------------------------------------------------
----------------------------Goat Classified population in grid----------------------------
------------------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION assign_population_categories (input_table TEXT, input_column TEXT, output_table TEXT, output_column TEXT, base_grid text)
RETURNS void
LANGUAGE plpgsql
AS $function$
BEGIN
	DROP TABLE IF EXISTS grouped_array;
	CREATE TABLE grouped_array (grid_id int4, pop_age_groups integer[]);
	
	EXECUTE '
	INSERT INTO grouped_array(
	SELECT grid_id, '|| quote_ident(input_column) ||' AS categorized_values FROM grid_500 g
	JOIN '|| quote_ident(input_table) ||' p   
	ON ST_Intersects(g.geom, st_centroid(p.geom)))';

	DROP TABLE IF EXISTS population_array_per_hexagon;
	CREATE TABLE population_array_per_hexagon (LIKE grouped_array INCLUDING all);

	EXECUTE 'INSERT INTO population_array_per_hexagon (
	select grid_id, array_agg(elem order by ordinality) AS outputs 
	from (
	   	select grid_id, ordinality, sum(elem) as elem
    	from grouped_array
    	cross join unnest('|| quote_ident(input_column) ||') with ordinality as u(elem, ordinality)
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
	SELECT g.*, p.pop_age_groups AS pop_array FROM '||quote_ident(base_grid)||' g
	LEFT JOIN population_array_per_hexagon p
	ON g.grid_id = p.grid_id)';

END;
$function$;


SELECT assign_population_categories('population_classificated_array', 'pop_age_groups', 'grid_500_age', 'array_ages','grid_500');
SELECT * FROM grid_500_age;


SELECT assign_population_categories('population_classificated_array', 'pop_gender_array', 'grid_500_age_gender', 'array_gender','grid_500_age');


SELECT * FROM population_classificated_array;
