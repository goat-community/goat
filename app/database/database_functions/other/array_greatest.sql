CREATE OR REPLACE FUNCTION array_greatest(anyarray)
RETURNS anyelement
LANGUAGE SQL
AS $$
  SELECT max(elements) FROM unnest($1) elements
$$;