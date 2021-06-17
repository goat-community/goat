CREATE OR REPLACE FUNCTION sum_int_array(arr integer[])
RETURNS integer AS
$$
	SELECT sum(v)::integer
	FROM (SELECT UNNEST(arr) v) x; 
$$
LANGUAGE sql immutable;	