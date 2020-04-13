CREATE OR REPLACE FUNCTION intersect_arrays(anyarray, anyarray)
RETURNS anyarray AS
$$
SELECT array(
SELECT unnest($1)
EXCEPT
SELECT unnest($2)
);
$$
LANGUAGE sql immutable;

--SELECT intersect_arrays(array['t','y','x'],array['t'])