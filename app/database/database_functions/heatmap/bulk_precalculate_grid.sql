DROP FUNCTION IF EXISTS bulk_precalculate_grid;
CREATE OR REPLACE FUNCTION bulk_precalculate_grid(grid text, number_bulk integer)
RETURNS SETOF integer 
LANGUAGE plpgsql
AS $function$
DECLARE 
count_grids integer;
upper_border integer :=0;
lower_border integer;
BEGIN 
	DROP TABLE IF EXISTS grid_ordered;
	CREATE temp TABLE grid_ordered AS 
	SELECT starting_points, grid_id
	FROM (
		SELECT ARRAY[ST_X(st_centroid(geom))::numeric,ST_Y(ST_Centroid(geom))::numeric] starting_points, grid_id 
		FROM grid_500 
		ORDER BY st_centroid(geom)
		LIMIT 1000
	) x;
	ALTER TABLE grid_ordered ADD COLUMN id serial;
	ALTER TABLE grid_ordered ADD PRIMARY key(id);
	
	SELECT count(*)
	INTO count_grids
	FROM grid_ordered;

	LOOP
    	lower_border = upper_border+1;
    	upper_border = upper_border+number_bulk;
    	
    	EXECUTE format ('
		WITH x AS 
    	(
    		SELECT array_agg(starting_points) AS array_starting_points, array_agg(grid_id) AS grid_ids
			FROM grid_ordered 
			WHERE id BETWEEN '||lower_border||' AND '||upper_border||'
    	)
		SELECT precalculate_grid('''||grid||''',15, x.array_starting_points, 83.33, x.grid_ids) 
		FROM x;');

		IF upper_border > count_grids THEN
		        EXIT;  -- exit loop
		    END IF;
		END LOOP;
	
END 
$function$;