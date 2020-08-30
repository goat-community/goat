CREATE OR REPLACE FUNCTION create_series_array(arr_length integer, arr_value integer)
RETURNS SETOF integer[] AS
$$
	SELECT ARRAY_AGG(arr_value)
	FROM 
	(
		SELECT generate_series(1,arr_length)*arr_value AS arr_value
	) x; 
$$
LANGUAGE sql immutable;